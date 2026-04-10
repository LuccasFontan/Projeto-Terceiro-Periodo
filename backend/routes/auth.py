from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db
from backend.models import Perfil, TokenBlocklist, Usuario
from backend.responses import created, error, success
from backend.services.audit import registrar_atividade
from backend.services.auth_service import (
    PROFILE_REDIRECTS,
    autenticar_login,
    buscar_perfil,
    criar_tokens,
    registrar_login,
    registrar_logout,
    renovar_usuario_por_refresh,
    revogar_token_atual,
    serializar_usuario,
    senha_segura,
)


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

PROFILE_REDIRECTS = {
    'administrador': '/pages/menus/administrador/menuAdministrador.html',
    'secretaria': '/pages/menus/secretaria/menuSecretariaEscolar.html',
    'psicopedagogo': '/pages/menus/psicopedagogo/menuPsicopedagogo.html',
    'professor': '/pages/menus/secretaria/menuSecretariaEscolar.html',
    'diretor': '/pages/menus/administrador/menuAdministrador.html',
}


def _serializar_usuario(usuario: Usuario) -> dict:
    return {
        'id': usuario.id,
        'nome': usuario.nome_completo,
        'email': usuario.email,
        'perfil': usuario.perfil.nome if usuario.perfil else None,
        'unidade_id': usuario.unidade_id,
        'unidade_nome': usuario.unidade.nome if usuario.unidade else None,
    }


def _buscar_perfil(nome_ou_id: str | int | None) -> Perfil | None:
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


def _criar_tokens(usuario: Usuario) -> dict:
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


def _revogar_token_atual() -> None:
    claims = get_jwt()
    token = TokenBlocklist(jti=claims['jti'])
    if claims.get('sub'):
        token.usuario_id = int(claims['sub'])
    db.session.add(token)


@auth_bp.post('/login')
def login():
    payload = request.get_json(silent=True) or request.form
    email = (payload.get('email') or '').strip().lower()
    senha = payload.get('senha') or ''

    if not email or not senha:
        return error('Informe email e senha.', 400, 'VALIDATION_ERROR')

    usuario = autenticar_login(email, senha)

    if usuario is None:
        return error('Credenciais invalidas.', 401, 'INVALID_CREDENTIALS')

    redirect_url = PROFILE_REDIRECTS.get(usuario.perfil.nome, '/index.html')
    tokens = criar_tokens(usuario, create_access_token=create_access_token, create_refresh_token=create_refresh_token)
    registrar_login(usuario)

    return success(
        message='Login realizado com sucesso.',
        data={
            'redirect_url': redirect_url,
            'token_type': 'Bearer',
            **tokens,
            'user': serializar_usuario(usuario),
        },
    )


@auth_bp.post('/logout')
@jwt_required()
def logout():
    revogar_token_atual(get_jwt)
    registrar_logout(get_jwt, get_jwt_identity)
    return success('Logout realizado com sucesso.', data={'redirect_url': '/index.html'})


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh_token():
    usuario = renovar_usuario_por_refresh(int(get_jwt_identity()))

    if usuario is None:
        return error('Credenciais invalidas.', 401, 'INVALID_CREDENTIALS')

    revogar_token_atual(get_jwt)
    db.session.commit()

    tokens = criar_tokens(usuario, create_access_token=create_access_token, create_refresh_token=create_refresh_token)
    return success(
        message='Token renovado com sucesso.',
        data={
            'token_type': 'Bearer',
            **tokens,
            'user': serializar_usuario(usuario),
        },
    )


@auth_bp.get('/me')
@jwt_required()
def me():
    claims = get_jwt()
    return success(
        'Sessao validada com sucesso.',
        data={
            'authenticated': True,
            'user_id': int(claims['sub']),
            'user_name': claims.get('nome'),
            'profile_name': claims.get('perfil'),
            'redirect_url': PROFILE_REDIRECTS.get(claims.get('perfil'), '/index.html'),
        },
    )


@auth_bp.post('/register')
def register():
    payload = request.get_json(silent=True) or {}

    nome = str(payload.get('nome') or payload.get('nome_completo') or '').strip()
    email = str(payload.get('email') or '').strip().lower()
    senha = str(payload.get('senha') or '')
    perfil = buscar_perfil(payload.get('perfil_id') or payload.get('perfil_nome') or payload.get('perfil') or 'administrador')

    if not nome or not email or not senha:
        return error('Informe nome, email e senha.', 400, 'VALIDATION_ERROR')
    if len(senha) < 8:
        return error('A senha deve ter no minimo 8 caracteres.', 400, 'VALIDATION_ERROR')
    if perfil is None:
        return error('Perfil invalido.', 400, 'INVALID_PROFILE')

    if Usuario.query.filter(db.func.lower(Usuario.email) == email, Usuario.deleted_at.is_(None)).first():
        return error('Email ja cadastrado.', 409, 'CONFLICT')

    usuario = Usuario(
        nome_completo=nome,
        cpf=str(payload.get('cpf') or email.split('@')[0]).strip(),
        email=email,
        matricula=str(payload.get('matricula') or email).strip(),
        senha_hash=senha_segura(senha),
        perfil_id=perfil.id,
        unidade_id=payload.get('unidade_id'),
        status=payload.get('status') or 'ativo',
    )
    db.session.add(usuario)
    db.session.commit()

    return created('Usuario registrado com sucesso.', data={'user': serializar_usuario(usuario)})
