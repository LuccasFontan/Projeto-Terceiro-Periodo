from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from backend.responses import error, success
from backend.security import jwt_required_admin
from backend.services.admin_panel_service import (
    atualizar_parametros_service,
    listar_alunos_service,
    obter_parametros_service,
    obter_relatorios_dashboard_service,
)


admin_extra_bp = Blueprint('admin_extra', __name__, url_prefix='/api/admin')


@admin_extra_bp.get('/relatorios/dashboard')
@jwt_required_admin
def relatorios_dashboard():
    return success('Relatorios carregados com sucesso.', data=obter_relatorios_dashboard_service())


@admin_extra_bp.get('/parametros')
@jwt_required_admin
def parametros():
    return success('Parametros carregados com sucesso.', data=obter_parametros_service())


@admin_extra_bp.put('/parametros')
@jwt_required_admin
def atualizar_parametros():
    payload = request.get_json(silent=True) or {}
    return success('Parametros atualizados com sucesso.', data=atualizar_parametros_service(payload))


@admin_extra_bp.get('/alunos')
@jwt_required_admin
def alunos():
    page = max(1, request.args.get('page', default=1, type=int))
    limit = min(max(1, request.args.get('limit', default=20, type=int)), 100)
    q = (request.args.get('q') or '').strip()
    unidade_id = request.args.get('unidade_id', type=int)
    serie = request.args.get('serie')
    diagnostico = request.args.get('diagnostico')
    status = request.args.get('status')

    return success(
        'Alunos carregados com sucesso.',
        data=listar_alunos_service(
            page=page,
            limit=limit,
            q=q or None,
            unidade_id=unidade_id,
            serie=serie,
            diagnostico=diagnostico,
            status=status,
        ),
    )
