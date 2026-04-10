from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError

from backend.responses import created, error, success
from backend.security import jwt_required_admin
from backend.services.unidades_service import (
    atualizar_unidade_service,
    buscar_unidade_service,
    criar_unidade_service,
    deletar_unidade_service,
    listar_unidades_service,
    registrar_atividade_unidade,
    serializar_unidade,
)


admin_unidades_bp = Blueprint('admin_unidades', __name__, url_prefix='/api/admin/unidades')


@admin_unidades_bp.get('')
@jwt_required_admin
def listar_unidades():
    incluir_excluidas = request.args.get('incluir_excluidas', 'false').lower() == 'true'
    status = request.args.get('status')
    q = (request.args.get('q') or '').strip()
    page = max(1, request.args.get('page', default=1, type=int))
    limit = min(max(1, request.args.get('limit', default=20, type=int)), 100)
    return success('Unidades carregadas com sucesso.', data=listar_unidades_service(incluir_excluidas, status, q, page, limit))


@admin_unidades_bp.get('/<int:unidade_id>')
@jwt_required_admin
def buscar_unidade(unidade_id: int):
    unidade = buscar_unidade_service(unidade_id)
    return success('Unidade carregada com sucesso.', data=serializar_unidade(unidade))


@admin_unidades_bp.post('')
@jwt_required_admin
def criar_unidade():
    payload = request.get_json(silent=True) or {}

    obrigatorios = ['nome', 'sigla', 'cnpj', 'email']
    faltantes = [campo for campo in obrigatorios if not payload.get(campo)]
    if faltantes:
        return error(f'Campos obrigatorios: {", ".join(faltantes)}', 400, 'VALIDATION_ERROR')

    try:
        unidade = criar_unidade_service(payload)
    except IntegrityError:
        return error('Nao foi possivel criar unidade. Verifique CNPJ e nome/sigla duplicados.', 409, 'CONFLICT')
    except ValueError as exc:
        return error(str(exc), 400, 'VALIDATION_ERROR')

    registrar_atividade_unidade(int(get_jwt_identity()), 'create', unidade)
    return created('Unidade criada com sucesso.', data={'item': serializar_unidade(unidade)})


@admin_unidades_bp.put('/<int:unidade_id>')
@jwt_required_admin
def atualizar_unidade(unidade_id: int):
    unidade = buscar_unidade_service(unidade_id)
    payload = request.get_json(silent=True) or {}
    try:
        unidade = atualizar_unidade_service(unidade, payload)
    except IntegrityError:
        return error('Nao foi possivel atualizar unidade. Verifique conflitos de dados.', 409, 'CONFLICT')

    registrar_atividade_unidade(int(get_jwt_identity()), 'update', unidade)
    return success('Unidade atualizada com sucesso.', data={'item': serializar_unidade(unidade)})


@admin_unidades_bp.delete('/<int:unidade_id>')
@jwt_required_admin
def deletar_unidade(unidade_id: int):
    unidade = buscar_unidade_service(unidade_id)
    unidade = deletar_unidade_service(unidade)
    registrar_atividade_unidade(int(get_jwt_identity()), 'delete', unidade)

    return success('Unidade removida com sucesso (soft delete).')
