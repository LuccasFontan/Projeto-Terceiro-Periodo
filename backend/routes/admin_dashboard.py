from __future__ import annotations

from flask import Blueprint, request
from backend.responses import success
from backend.security import jwt_required_admin
from backend.services.dashboard_service import (
    obter_indicadores_dashboard,
    obter_status_sistema,
)
from backend.services.admin_panel_service import listar_auditoria_service


admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/api/admin')


@admin_dashboard_bp.get('/dashboard')
@jwt_required_admin
def dashboard():
    return success('Dashboard carregado com sucesso.', data=obter_indicadores_dashboard())


@admin_dashboard_bp.get('/atividades-recentes')
@jwt_required_admin
def atividades_recentes():
    limite = request.args.get('limit', default=10, type=int)
    pagina = request.args.get('page', default=1, type=int)
    usuario = request.args.get('usuario')
    acao = request.args.get('acao') or request.args.get('tipo')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    return success(
        'Atividades recentes carregadas com sucesso.',
        data=listar_auditoria_service(
            page=pagina,
            limit=limite,
            usuario=usuario,
            acao=acao,
            data_inicio=data_inicio,
            data_fim=data_fim,
        ),
    )


@admin_dashboard_bp.get('/status-sistema')
@jwt_required_admin
def status_sistema():
    return success('Status do sistema carregado com sucesso.', data=obter_status_sistema())


@admin_dashboard_bp.get('/auditoria')
@jwt_required_admin
def auditoria():
    return atividades_recentes()
