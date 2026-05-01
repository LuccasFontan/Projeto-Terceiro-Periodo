from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from schemas.admin_schemas import UsuarioSchema

from backend.responses import created, error, success
from backend.security import jwt_required_admin
from backend.services.usuarios_service import (
    atualizar_usuario_service,
    buscar_usuario_service,
    criar_usuario_service,
    deletar_usuario_service,
    listar_usuarios_service,
    registrar_atividade_usuario,
    serializar_usuario,
)


admin_usuarios_bp = Blueprint('admin_usuarios', __name__, url_prefix='/api/admin/usuarios')


@admin_usuarios_bp.get('')
@jwt_required_admin
def listar_usuarios():
    incluir_excluidos = request.args.get('incluir_excluidos', 'false').lower() == 'true'
    status = request.args.get('status')
    perfil = request.args.get('perfil')
    unidade_id = request.args.get('unidade_id', type=int)
    q = (request.args.get('q') or '').strip()
    page = max(1, request.args.get('page', default=1, type=int))
    limit = min(max(1, request.args.get('limit', default=20, type=int)), 100)
    return success('Usuarios carregados com sucesso.', data=listar_usuarios_service(incluir_excluidos, status, perfil, unidade_id, q, page, limit))


@admin_usuarios_bp.get('/<int:usuario_id>')
@jwt_required_admin
def buscar_usuario(usuario_id: int):
    usuario = buscar_usuario_service(usuario_id)
    return success('Usuario carregado com sucesso.', data=serializar_usuario(usuario))


@admin_usuarios_bp.post('')
@jwt_required_admin
def criar_usuario():
    payload = request.get_json(silent=True) or {}
    try:
        dados = UsuarioSchema(**payload)
    except ValidationError as e:
        return error('Dados inválidos.', 400, 'VALIDATION_ERROR', details=e.errors())

    try:
        usuario = criar_usuario_service(dados.model_dump(exclude_none=True))
    except IntegrityError:
        return error('Nao foi possivel criar usuario. Verifique CPF, email ou matricula duplicados.', 409, 'CONFLICT')
    except ValueError as exc:
        return error(str(exc), 400, 'VALIDATION_ERROR')

    registrar_atividade_usuario(int(get_jwt_identity()), 'create', usuario)
    return created('Usuario criado com sucesso.', data={'item': serializar_usuario(usuario)})


@admin_usuarios_bp.put('/<int:usuario_id>')
@jwt_required_admin
def atualizar_usuario(usuario_id: int):
    usuario = buscar_usuario_service(usuario_id)
    payload = request.get_json(silent=True) or {}
    try:
        usuario = atualizar_usuario_service(usuario, payload)
    except IntegrityError:
        return error('Nao foi possivel atualizar usuario. Verifique conflitos de dados.', 409, 'CONFLICT')
    except ValueError as exc:
        return error(str(exc), 400, 'VALIDATION_ERROR')

    registrar_atividade_usuario(int(get_jwt_identity()), 'update', usuario)
    return success('Usuario atualizado com sucesso.', data={'item': serializar_usuario(usuario)})


@admin_usuarios_bp.delete('/<int:usuario_id>')
@jwt_required_admin
def deletar_usuario(usuario_id: int):
    usuario = buscar_usuario_service(usuario_id)
    usuario = deletar_usuario_service(usuario)
    registrar_atividade_usuario(int(get_jwt_identity()), 'delete', usuario)

    return success('Usuario removido com sucesso (soft delete).')
