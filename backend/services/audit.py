from __future__ import annotations

from backend.extensions import db
from backend.models import Auditoria


def registrar_atividade(
    usuario_id: int | None,
    acao: str,
    entidade: str,
    entidade_id: int | None = None,
    detalhes: dict | None = None,
    ip_origem: str | None = None,
    user_agent: str | None = None,
) -> Auditoria:
    registro = Auditoria(
        usuario_id=usuario_id,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhes=detalhes or {},
        ip_origem=ip_origem,
        user_agent=user_agent,
    )
    db.session.add(registro)
    return registro
