from __future__ import annotations

from datetime import datetime, timezone

from flask import request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from backend.extensions import db
from backend.models import Perfil, Usuario
from backend.services.audit import registrar_atividade


def serializar_usuario(usuario: Usuario) -> dict:
    return {
        'id': usuario.id,
        'unidade_id': usuario.unidade_id,
        'perfil_id': usuario.perfil_id,
        'perfil_nome': usuario.perfil.nome if usuario.perfil else None,
        'nome_completo': usuario.nome_completo,
        'cpf': usuario.cpf,
        'email': usuario.email,
        'telefone': usuario.telefone,
        'matricula': usuario.matricula,
        'departamento': usuario.departamento,
        'status': usuario.status,
        'data_admissao': usuario.data_admissao.isoformat() if usuario.data_admissao else None,
        'ultimo_login_em': usuario.ultimo_login_em.isoformat() if usuario.ultimo_login_em else None,
        'created_at': usuario.created_at.isoformat() if usuario.created_at else None,
        'updated_at': usuario.updated_at.isoformat() if usuario.updated_at else None,
        'deleted_at': usuario.deleted_at.isoformat() if usuario.deleted_at else None,
    }


def buscar_perfil(payload: dict) -> Perfil | None:
    perfil_id = payload.get('perfil_id')
    perfil_nome = payload.get('perfil_nome')

    if perfil_id:
        return Perfil.query.get(perfil_id)

    if perfil_nome:
        return Perfil.query.filter(db.func.lower(Perfil.nome) == str(perfil_nome).strip().lower()).first()

    return None


def listar_usuarios_service(incluir_excluidos: bool, status: str | None, perfil: str | None, unidade_id: int | None, q: str, page: int, limit: int) -> dict:
    query = Usuario.query.join(Usuario.perfil)

    if not incluir_excluidos:
        query = query.filter(Usuario.deleted_at.is_(None))

    if status:
        query = query.filter(Usuario.status == status)

    if perfil:
        query = query.filter(db.func.lower(Perfil.nome) == perfil.lower())

    if unidade_id is not None:
        query = query.filter(Usuario.unidade_id == unidade_id)

    if q:
        termo = f'%{q.lower()}%'
        query = query.filter(
            or_(
                db.func.lower(Usuario.nome_completo).like(termo),
                db.func.lower(Usuario.email).like(termo),
                db.func.lower(Usuario.matricula).like(termo),
            )
        )

    total = query.count()
    usuarios = query.order_by(Usuario.nome_completo.asc()).offset((page - 1) * limit).limit(limit).all()
    return {'items': [serializar_usuario(u) for u in usuarios], 'total': total, 'page': page, 'limit': limit}


def buscar_usuario_service(usuario_id: int) -> Usuario:
    return Usuario.query.get_or_404(usuario_id)


def criar_usuario_service(payload: dict) -> Usuario:
    perfil = buscar_perfil(payload)
    if perfil is None:
        raise ValueError('Perfil invalido. Informe perfil_id ou perfil_nome valido.')

    senha = str(payload.get('senha'))
    if len(senha) < 8:
        raise ValueError('A senha deve ter no minimo 8 caracteres.')

    usuario = Usuario(
        unidade_id=payload.get('unidade_id'),
        perfil_id=perfil.id,
        nome_completo=str(payload.get('nome_completo')).strip(),
        cpf=str(payload.get('cpf')).strip(),
        email=str(payload.get('email')).strip().lower(),
        telefone=payload.get('telefone'),
        matricula=str(payload.get('matricula')).strip(),
        senha_hash=generate_password_hash(senha),
        departamento=payload.get('departamento'),
        status=payload.get('status') or 'ativo',
        data_admissao=payload.get('data_admissao'),
        enviar_email_boas_vindas=bool(payload.get('enviar_email_boas_vindas', True)),
    )

    db.session.add(usuario)
    db.session.commit()
    return usuario


def atualizar_usuario_service(usuario: Usuario, payload: dict) -> Usuario:
    perfil = buscar_perfil(payload)
    if ('perfil_id' in payload or 'perfil_nome' in payload) and perfil is None:
        raise ValueError('Perfil invalido. Informe perfil_id ou perfil_nome valido.')

    campos_permitidos = [
        'unidade_id', 'nome_completo', 'cpf', 'email', 'telefone', 'matricula',
        'departamento', 'status', 'data_admissao', 'enviar_email_boas_vindas',
    ]

    for campo in campos_permitidos:
        if campo in payload:
            valor = payload[campo]
            if isinstance(valor, str):
                valor = valor.strip()
            if campo == 'email' and isinstance(valor, str):
                valor = valor.lower()
            setattr(usuario, campo, valor)

    if perfil is not None:
        usuario.perfil_id = perfil.id

    if payload.get('senha'):
        senha = str(payload.get('senha'))
        if len(senha) < 8:
            raise ValueError('A senha deve ter no minimo 8 caracteres.')
        usuario.senha_hash = generate_password_hash(senha)

    db.session.commit()
    return usuario


def deletar_usuario_service(usuario: Usuario) -> Usuario:
    if usuario.deleted_at is None:
        usuario.deleted_at = datetime.now(timezone.utc)
        usuario.status = 'inativo'
        db.session.commit()
    return usuario


def registrar_atividade_usuario(usuario_id: int, acao: str, usuario: Usuario) -> None:
    registrar_atividade(
        usuario_id,
        acao,
        'usuario',
        usuario.id,
        detalhes={'email': usuario.email, 'perfil_id': usuario.perfil_id},
        ip_origem=request.headers.get('X-Forwarded-For', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
    )
    db.session.commit()
