from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from backend.extensions import db
from backend.models import (
    Aluno,
    AnoLetivo,
    Auditoria,
    CategoriaNeurodiversidade,
    Encaminhamento,
    Laudo,
    ParametroSistema,
    Relatorio,
    Triagem,
    Unidade,
    Usuario,
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None


def _parse_json_or_text(value: Any) -> Any:
    return value if isinstance(value, dict) else value


def serializar_auditoria(item: Auditoria) -> dict:
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


def listar_auditoria_service(
    page: int = 1,
    limit: int = 10,
    usuario: str | None = None,
    acao: str | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> dict:
    query = Auditoria.query.options(joinedload(Auditoria.usuario)).order_by(Auditoria.created_at.desc())

    if usuario:
        termo = f'%{usuario.lower()}%'
        query = query.join(Usuario, Auditoria.usuario_id == Usuario.id, isouter=True).filter(
            or_(
                func.lower(Usuario.nome_completo).like(termo),
                func.lower(Usuario.email).like(termo),
            )
        )

    if acao:
        query = query.filter(func.lower(Auditoria.acao) == acao.lower())

    inicio = _parse_date(data_inicio)
    fim = _parse_date(data_fim)
    if inicio:
        query = query.filter(func.date(Auditoria.created_at) >= inicio)
    if fim:
        query = query.filter(func.date(Auditoria.created_at) <= fim)

    total = query.count()
    itens = query.offset((page - 1) * limit).limit(limit).all()
    resumo = {
        'totalAcoes': total,
        'criacoes': Auditoria.query.filter(func.lower(Auditoria.acao) == 'create').count(),
        'atualizacoes': Auditoria.query.filter(func.lower(Auditoria.acao) == 'update').count(),
        'exclusoes': Auditoria.query.filter(func.lower(Auditoria.acao) == 'delete').count(),
        'logins': Auditoria.query.filter(func.lower(Auditoria.acao) == 'login').count(),
        'logouts': Auditoria.query.filter(func.lower(Auditoria.acao) == 'logout').count(),
    }

    return {
        'items': [serializar_auditoria(item) for item in itens],
        'total': total,
        'page': page,
        'limit': limit,
        'resumo': resumo,
    }


def _serie_bucket(serie: str | None) -> str:
    texto = (serie or '').strip().lower()
    if not texto:
        return '6ao9ano'
    if any(palavra in texto for palavra in ['infantil', 'ei', 'creche', 'pre']):
        return 'educacaoInfantil'
    if any(palavra in texto for palavra in ['1º', '1°', '1 ano', '1-3', '1a3', '1 ao 3', '1o ao 3', '1º ao 3']):
        return '1ao3ano'
    if any(palavra in texto for palavra in ['4º', '4°', '4 ano', '4-5', '4a5', '4 ao 5', '4º ao 5']):
        return '4ao5ano'
    return '6ao9ano'


def obter_relatorios_dashboard_service() -> dict:
    alunos = Aluno.query.options(joinedload(Aluno.unidade), joinedload(Aluno.categorias)).filter(Aluno.deleted_at.is_(None)).all()
    total_alunos = len(alunos)
    com_laudos = sum(1 for aluno in alunos if getattr(aluno, 'laudos', None))
    em_acompanhamento = sum(1 for aluno in alunos if (aluno.status or '').lower() in {'acompanhamento', 'em_acompanhamento'})
    encaminhamentos_pendentes = Encaminhamento.query.filter(func.lower(Encaminhamento.status).in_(['aberto', 'pendente'])).count()

    distribuicao = defaultdict(int)
    for aluno in alunos:
        categorias = [categoria.nome for categoria in getattr(aluno, 'categorias', [])]
        if categorias:
            for categoria in categorias:
                distribuicao[categoria] += 1
        else:
            distribuicao['Outros'] += 1

    series = defaultdict(int)
    for aluno in alunos:
        bucket = _serie_bucket(aluno.serie_turma)
        series[bucket] += 1

    resumo_por_unidade: list[dict[str, Any]] = []
    for unidade in Unidade.query.filter(Unidade.deleted_at.is_(None)).order_by(Unidade.nome.asc()).all():
        alunos_unidade = [aluno for aluno in alunos if aluno.unidade_id == unidade.id]
        total_unidade = len(alunos_unidade)
        if total_unidade == 0:
            continue
        com_laudos_unidade = sum(1 for aluno in alunos_unidade if getattr(aluno, 'laudos', None))
        em_acompanhamento_unidade = sum(1 for aluno in alunos_unidade if (aluno.status or '').lower() in {'acompanhamento', 'em_acompanhamento'})
        resumo_por_unidade.append(
            {
                'nomeUnidade': unidade.nome,
                'totalAlunos': total_unidade,
                'comLaudos': com_laudos_unidade,
                'emAcompanhamento': em_acompanhamento_unidade,
                'taxaAbrangencia': round((com_laudos_unidade / total_unidade) * 100, 1) if total_unidade else 0,
            }
        )

    return {
        'totalAlunos': total_alunos,
        'comLaudos': com_laudos,
        'emAcompanhamento': em_acompanhamento,
        'encaminhamentosPendentes': encaminhamentos_pendentes,
        'distribuicaoNeurodiversidade': dict(sorted(distribuicao.items())),
        'alunosPorSerie': {
            'educacaoInfantil': series.get('educacaoInfantil', 0),
            '1ao3ano': series.get('1ao3ano', 0),
            '4ao5ano': series.get('4ao5ano', 0),
            '6ao9ano': series.get('6ao9ano', 0),
        },
        'resumoPorUnidade': resumo_por_unidade,
    }


def serializar_aluno(aluno: Aluno) -> dict:
    categorias = [categoria.nome for categoria in getattr(aluno, 'categorias', [])]
    return {
        'id': aluno.id,
        'nome': aluno.nome_completo,
        'matricula': f'ALU-{aluno.id:06d}',
        'cpf': aluno.cpf,
        'unidade_id': aluno.unidade_id,
        'unidade': aluno.unidade.nome if aluno.unidade else None,
        'serie': aluno.serie_turma,
        'diagnostico': ', '.join(categorias) if categorias else 'Sem diagnóstico',
        'status': aluno.status,
        'data_nascimento': aluno.data_nascimento.isoformat() if aluno.data_nascimento else None,
        'responsavel_nome': aluno.responsavel_nome,
        'responsavel_telefone': aluno.responsavel_telefone,
        'nivel_suporte': aluno.nivel_suporte,
        'tem_laudo': bool(getattr(aluno, 'laudos', [])),
    }


def listar_alunos_service(
    page: int = 1,
    limit: int = 20,
    q: str | None = None,
    unidade_id: int | None = None,
    serie: str | None = None,
    diagnostico: str | None = None,
    status: str | None = None,
) -> dict:
    query = Aluno.query.options(joinedload(Aluno.unidade), joinedload(Aluno.categorias), joinedload(Aluno.laudos)).filter(Aluno.deleted_at.is_(None))

    if unidade_id is not None:
        query = query.filter(Aluno.unidade_id == unidade_id)
    if serie:
        query = query.filter(func.lower(Aluno.serie_turma) == serie.lower())
    if status:
        query = query.filter(func.lower(Aluno.status) == status.lower())
    if diagnostico:
        query = query.join(Aluno.categorias).filter(func.lower(CategoriaNeurodiversidade.nome) == diagnostico.lower())
    if q:
        termo = f'%{q.lower()}%'
        query = query.filter(
            or_(
                func.lower(Aluno.nome_completo).like(termo),
                func.lower(Aluno.cpf).like(termo),
                func.cast(Aluno.id, db.String).like(termo),
            )
        )

    total = query.distinct(Aluno.id).count()
    alunos = query.order_by(Aluno.nome_completo.asc()).offset((page - 1) * limit).limit(limit).all()

    items = [serializar_aluno(aluno) for aluno in alunos]
    return {
        'items': items,
        'total': total,
        'page': page,
        'limit': limit,
        'resumo': {
            'totalAlunos': total,
            'comDiagnostico': sum(1 for aluno in alunos if aluno.categorias),
            'emAcompanhamento': sum(1 for aluno in alunos if (aluno.status or '').lower() in {'acompanhamento', 'em_acompanhamento'}),
            'inativos': sum(1 for aluno in alunos if (aluno.status or '').lower() == 'inativo'),
        },
    }


def obter_parametros_service() -> dict:
    anos_letivos = AnoLetivo.query.order_by(AnoLetivo.ano.desc()).all()
    categorias = CategoriaNeurodiversidade.query.order_by(CategoriaNeurodiversidade.nome.asc()).all()
    params = {parametro.chave: parametro for parametro in ParametroSistema.query.all()}

    email_config = params.get('email.smtp')
    sistema_config = params.get('sistema.geral')

    return {
        'anosLetivos': [
            {
                'id': ano.id,
                'ano': ano.ano,
                'status': ano.status,
                'data_inicio': ano.data_inicio.isoformat() if ano.data_inicio else None,
                'data_fim': ano.data_fim.isoformat() if ano.data_fim else None,
            }
            for ano in anos_letivos
        ],
        'categorias': [
            {
                'id': categoria.id,
                'nome': categoria.nome,
                'descricao': categoria.descricao,
                'ativa': categoria.ativa,
            }
            for categoria in categorias
        ],
        'emailConfig': (email_config.valor_json if email_config else {}),
        'sistemaConfig': (sistema_config.valor_json if sistema_config else {}),
    }


def atualizar_parametros_service(payload: dict) -> dict:
    email_config = payload.get('emailConfig') or payload.get('email') or {}
    sistema_config = payload.get('sistemaConfig') or payload.get('sistema') or {}

    email_parametro = ParametroSistema.query.filter_by(chave='email.smtp').first()
    if email_parametro is None:
        email_parametro = ParametroSistema(chave='email.smtp', valor_json={})
        db.session.add(email_parametro)
    email_parametro.valor_json = _parse_json_or_text(email_config)
    email_parametro.descricao = 'Configuracao SMTP padrao'

    sistema_parametro = ParametroSistema.query.filter_by(chave='sistema.geral').first()
    if sistema_parametro is None:
        sistema_parametro = ParametroSistema(chave='sistema.geral', valor_json={})
        db.session.add(sistema_parametro)
    sistema_parametro.valor_json = _parse_json_or_text(sistema_config)
    sistema_parametro.descricao = 'Configuracoes gerais do sistema'

    db.session.commit()
    return obter_parametros_service()
