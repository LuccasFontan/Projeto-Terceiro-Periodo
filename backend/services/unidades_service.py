from __future__ import annotations

from datetime import datetime, timezone

from flask import request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Unidade
from backend.services.audit import registrar_atividade


def serializar_unidade(unidade: Unidade) -> dict:
    return {
        'id': unidade.id,
        'nome': unidade.nome,
        'sigla': unidade.sigla,
        'cnpj': unidade.cnpj,
        'email': unidade.email,
        'telefone': unidade.telefone,
        'celular': unidade.celular,
        'rua': unidade.rua,
        'numero': unidade.numero,
        'complemento': unidade.complemento,
        'cidade': unidade.cidade,
        'estado': unidade.estado,
        'cep': unidade.cep,
        'diretor_nome': unidade.diretor_nome,
        'diretor_cpf': unidade.diretor_cpf,
        'diretor_email': unidade.diretor_email,
        'diretor_telefone': unidade.diretor_telefone,
        'status': unidade.status,
        'tipo_unidade': unidade.tipo_unidade,
        'capacidade_estudantes': unidade.capacidade_estudantes,
        'data_inicio_operacao': unidade.data_inicio_operacao.isoformat() if unidade.data_inicio_operacao else None,
        'observacoes': unidade.observacoes,
        'created_at': unidade.created_at.isoformat() if unidade.created_at else None,
        'updated_at': unidade.updated_at.isoformat() if unidade.updated_at else None,
        'deleted_at': unidade.deleted_at.isoformat() if unidade.deleted_at else None,
    }


def listar_unidades_service(incluir_excluidas: bool, status: str | None, q: str, page: int, limit: int) -> dict:
    query = Unidade.query

    if not incluir_excluidas:
        query = query.filter(Unidade.deleted_at.is_(None))

    if status:
        query = query.filter(Unidade.status == status)

    if q:
        termo = f'%{q.lower()}%'
        query = query.filter(
            or_(
                db.func.lower(Unidade.nome).like(termo),
                db.func.lower(Unidade.sigla).like(termo),
                db.func.lower(Unidade.email).like(termo),
                db.func.lower(Unidade.diretor_nome).like(termo),
            )
        )

    total = query.count()
    unidades = query.order_by(Unidade.nome.asc()).offset((page - 1) * limit).limit(limit).all()
    return {'items': [serializar_unidade(u) for u in unidades], 'total': total, 'page': page, 'limit': limit}


def buscar_unidade_service(unidade_id: int) -> Unidade:
    return Unidade.query.get_or_404(unidade_id)


def criar_unidade_service(payload: dict) -> Unidade:
    unidade = Unidade(
        nome=str(payload.get('nome')).strip(),
        sigla=str(payload.get('sigla')).strip(),
        cnpj=str(payload.get('cnpj')).strip(),
        email=str(payload.get('email')).strip().lower(),
        telefone=payload.get('telefone'),
        celular=payload.get('celular'),
        rua=payload.get('rua'),
        numero=payload.get('numero'),
        complemento=payload.get('complemento'),
        cidade=payload.get('cidade'),
        estado=payload.get('estado'),
        cep=payload.get('cep'),
        diretor_nome=payload.get('diretor_nome'),
        diretor_cpf=payload.get('diretor_cpf'),
        diretor_email=payload.get('diretor_email'),
        diretor_telefone=payload.get('diretor_telefone'),
        tipo_unidade=payload.get('tipo_unidade'),
        capacidade_estudantes=payload.get('capacidade_estudantes'),
        status=payload.get('status') or 'ativa',
        data_inicio_operacao=payload.get('data_inicio_operacao'),
        observacoes=payload.get('observacoes'),
    )

    db.session.add(unidade)
    db.session.commit()
    return unidade


def atualizar_unidade_service(unidade: Unidade, payload: dict) -> Unidade:
    campos_permitidos = [
        'nome', 'sigla', 'cnpj', 'email', 'telefone', 'celular', 'rua', 'numero',
        'complemento', 'cidade', 'estado', 'cep', 'diretor_nome', 'diretor_cpf',
        'diretor_email', 'diretor_telefone', 'tipo_unidade', 'capacidade_estudantes',
        'status', 'data_inicio_operacao', 'observacoes',
    ]

    for campo in campos_permitidos:
        if campo in payload:
            valor = payload[campo]
            if isinstance(valor, str):
                valor = valor.strip()
            if campo == 'email' and isinstance(valor, str):
                valor = valor.lower()
            setattr(unidade, campo, valor)

    db.session.commit()
    return unidade


def deletar_unidade_service(unidade: Unidade) -> Unidade:
    if unidade.deleted_at is None:
        unidade.deleted_at = datetime.now(timezone.utc)
        unidade.status = 'inativa'
        db.session.commit()
    return unidade


def registrar_atividade_unidade(usuario_id: int, acao: str, unidade: Unidade) -> None:
    registrar_atividade(
        usuario_id,
        acao,
        'unidade',
        unidade.id,
        detalhes={'cnpj': unidade.cnpj, 'sigla': unidade.sigla},
        ip_origem=request.headers.get('X-Forwarded-For', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
    )
    db.session.commit()
