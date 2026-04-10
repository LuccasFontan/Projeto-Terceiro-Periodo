from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text

from backend.extensions import db
from backend.models import Auditoria, TokenBlocklist, Unidade, Usuario


def serializar_atividade(item: Auditoria) -> dict:
    usuario_nome = item.usuario.nome_completo if item.usuario else None
    return {
        'id': item.id,
        'usuario_id': item.usuario_id,
        'usuario_nome': usuario_nome,
        'acao': item.acao,
        'entidade': item.entidade,
        'entidade_id': item.entidade_id,
        'detalhes': item.detalhes or {},
        'ip_origem': item.ip_origem,
        'created_at': item.created_at.isoformat() if item.created_at else None,
    }


def obter_indicadores_dashboard() -> dict:
    total_unidades = Unidade.query.filter(Unidade.deleted_at.is_(None)).count()
    usuarios_ativos = Usuario.query.filter(Usuario.deleted_at.is_(None), Usuario.status == 'ativo').count()
    configuracoes_pendentes = Unidade.query.filter(
        Unidade.deleted_at.is_(None),
        (Unidade.diretor_nome.is_(None)) | (Unidade.diretor_email.is_(None)) | (Unidade.telefone.is_(None)),
    ).count()
    alerta_seguranca = TokenBlocklist.query.count()

    return {
        'totalUnidades': total_unidades,
        'usuariosAtivos': usuarios_ativos,
        'configuracoesPendentes': configuracoes_pendentes,
        'alertaSeguranca': alerta_seguranca,
    }


def obter_atividades_recentes(limit: int = 10, page: int = 1) -> dict:
    limite = max(1, min(limit, 50))
    pagina = max(1, page)
    query = Auditoria.query.order_by(Auditoria.created_at.desc())
    total = query.count()
    itens = query.offset((pagina - 1) * limite).limit(limite).all()

    return {
        'items': [serializar_atividade(item) for item in itens],
        'total': total,
        'page': pagina,
        'limit': limite,
    }


def obter_status_sistema() -> dict:
    total_unidades = Unidade.query.filter(Unidade.deleted_at.is_(None)).count()
    usuarios_ativos = Usuario.query.filter(Usuario.deleted_at.is_(None), Usuario.status == 'ativo').count()
    ultima_atividade = Auditoria.query.order_by(Auditoria.created_at.desc()).first()

    try:
        resultado = db.session.execute(text('SELECT pg_size_pretty(pg_database_size(current_database()))'))
        tamanho = str(resultado.scalar() or 'indisponivel')
    except Exception:
        tamanho = 'indisponivel'

    return {
        'statusBancoDados': 'operacional',
        'textoBancoDados': 'PostgreSQL conectado com sucesso',
        'statusArmazenamento': 'operacional',
        'textoArmazenamento': f'Tamanho atual: {tamanho}',
        'textoSincronizacao': 'Dados atualizados sob demanda pela API',
        'tempoSincronizacao': ultima_atividade.created_at.isoformat() if ultima_atividade and ultima_atividade.created_at else datetime.now(timezone.utc).isoformat(),
        'totalUnidades': total_unidades,
        'usuariosAtivos': usuarios_ativos,
    }
