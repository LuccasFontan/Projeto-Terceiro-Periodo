from __future__ import annotations

from datetime import datetime, timezone

from flask import request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db
from backend.models import Perfil, TokenBlocklist, Usuario
from backend.services.audit import registrar_atividade

PROFILE_REDIRECTS = {
    'administrador': '/pages/menus/administrador/menuAdministrador.html',
    'secretaria': '/pages/menus/secretaria/menuSecretariaEscolar.html',
    'psicopedagogo': '/pages/menus/psicopedagogo/menuPsicopedagogo.html',
    'professor': '/pages/menus/secretaria/menuSecretariaEscolar.html',
    'diretor': '/pages/menus/administrador/menuAdministrador.html',
}


def serializar_usuario(usuario: Usuario) -> dict:
    return {
        'id': usuario.id,
        'nome': usuario.nome_completo,
        'email': usuario.email,
        'perfil': usuario.perfil.nome if usuario.perfil else None,
        'unidade_id': usuario.unidade_id,
        'unidade_nome': usuario.unidade.nome if usuario.unidade else None,
    }


def buscar_perfil(nome_ou_id: str | int | None) -> Perfil | None:
    if nome_ou_id is None:
        return None
    if isinstance(nome_ou_id, int):
        return Perfil.query.get(nome_ou_id)

    texto = str(nome_ou_id).strip()
    if not texto:
        return None

    if texto.isdigit():
        return Perfil.query.get(int(texto))

    return Perfil.query.filter(db.func.lower(Perfil.nome) == texto.lower()).first()


def criar_tokens(usuario: Usuario, create_access_token, create_refresh_token) -> dict:
    claims = {
        'perfil': usuario.perfil.nome if usuario.perfil else 'usuario',
        'nome': usuario.nome_completo,
        'email': usuario.email,
        'unidade_id': usuario.unidade_id,
    }
    return {
        'access_token': create_access_token(identity=str(usuario.id), additional_claims=claims),
        'refresh_token': create_refresh_token(identity=str(usuario.id), additional_claims=claims),
    }


def autenticar_login(email: str, senha: str) -> Usuario | None:
    usuario = (
        Usuario.query
        .join(Usuario.perfil)
        .filter(db.func.lower(Usuario.email) == email.lower(), Usuario.deleted_at.is_(None))
        .first()
    )

    if usuario is None or usuario.status != 'ativo':
        return None

    if not check_password_hash(usuario.senha_hash, senha):
        return None

    usuario.ultimo_login_em = datetime.now(timezone.utc)
    db.session.commit()
    return usuario


def registrar_login(usuario: Usuario) -> None:
    registrar_atividade(
        usuario.id,
        'login',
        'auth',
        detalhes={'email': usuario.email, 'perfil': usuario.perfil.nome if usuario.perfil else None},
        ip_origem=request.headers.get('X-Forwarded-For', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
    )
    db.session.commit()


def revogar_token_atual(get_jwt) -> TokenBlocklist:
    claims = get_jwt()
    token = TokenBlocklist(jti=claims['jti'])
    if claims.get('sub'):
        token.usuario_id = int(claims['sub'])
    db.session.add(token)
    return token


def registrar_logout(get_jwt, get_jwt_identity) -> None:
    claims = get_jwt()
    registrar_atividade(
        int(get_jwt_identity()) if get_jwt_identity() else None,
        'logout',
        'auth',
        detalhes={'jti': claims['jti']},
        ip_origem=request.headers.get('X-Forwarded-For', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
    )
    db.session.commit()


def renovar_usuario_por_refresh(usuario_id: int) -> Usuario | None:
    usuario = Usuario.query.filter(Usuario.id == usuario_id, Usuario.deleted_at.is_(None)).join(Usuario.perfil).first()
    if usuario is None or usuario.status != 'ativo':
        return None
    return usuario


def registrar_usuario(usuario: Usuario, payload: dict) -> None:
    db.session.add(usuario)
    db.session.commit()


def senha_segura(senha: str) -> str:
    return generate_password_hash(senha)
