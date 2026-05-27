/**
 * planosPsicopedagogo.js
 * Controlador do módulo de Planos de Acompanhamento para o Psicopedagogo.
 * Inclui: listagem, criação, visualização (V), edição (E) e exclusão (D).
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // Elementos DOM
  // -------------------------------------------------------------------------
  const nomeUsuarioEl     = document.getElementById('nomeUsuario');
  const nomeInstituicaoEl = document.querySelector('.nomeInstituicao');
  const btnSair           = document.getElementById('btnSair');

  // Métricas
  const totalPlanosEl          = document.getElementById('totalPlanos');
  const totalPlanosAtivosEl    = document.getElementById('totalPlanosAtivos');
  const totalPlanosConcluidosEl= document.getElementById('totalPlanosConcluidos');
  const totalPlanosSuspensosEl = document.getElementById('totalPlanosSuspensos');

  // Formulário de criação
  const formPlano          = document.getElementById('formPlano');
  const selectAluno        = document.getElementById('planoAluno');
  const inputTitulo        = document.getElementById('planoTitulo');
  const inputDataInicio    = document.getElementById('planoDataInicio');
  const inputDataFim       = document.getElementById('planoDataFim');
  const selectPeriodicidade= document.getElementById('planoPeriodicidade');
  const selectStatus       = document.getElementById('planoStatus');
  const textObjetivo       = document.getElementById('planoObjetivo');
  const textEstrategias    = document.getElementById('planoEstrategias');

  // Tabela e Paginação
  const tabelaPlanos = document.getElementById('tabelaPlanos');
  const tabelaBody   = tabelaPlanos ? tabelaPlanos.querySelector('tbody') : null;
  const paginacaoEl  = document.getElementById('paginacaoPlanos');

  let paginaAtual  = 1;
  const limiteItens = 10;

  // -------------------------------------------------------------------------
  // Modais Bootstrap
  // -------------------------------------------------------------------------
  let bsModalVer    = null;
  let bsModalEditar = null;
  let bsModalDeletar= null;
  let bsToast       = null;

  function inicializarModais() {
    const elVer    = document.getElementById('modalVerPlano');
    const elEditar = document.getElementById('modalEditarPlano');
    const elDeletar= document.getElementById('modalDeletarPlano');
    const elToast  = document.getElementById('toastAcao');

    if (elVer)    bsModalVer    = new bootstrap.Modal(elVer);
    if (elEditar) bsModalEditar = new bootstrap.Modal(elEditar);
    if (elDeletar)bsModalDeletar= new bootstrap.Modal(elDeletar);
    if (elToast)  bsToast       = new bootstrap.Toast(elToast, { delay: 3500 });
  }

  // -------------------------------------------------------------------------
  // Toast helper
  // -------------------------------------------------------------------------
  function exibirToast(mensagem, tipo = 'success') {
    const el = document.getElementById('toastAcao');
    const msg= document.getElementById('toastMensagem');
    if (!el || !msg || !bsToast) return;

    const icone = tipo === 'success'
      ? '<i class="bi bi-check-circle-fill"></i>'
      : '<i class="bi bi-exclamation-triangle-fill"></i>';

    el.className = `toast align-items-center text-white border-0 bg-${tipo === 'success' ? 'success' : 'danger'}`;
    el.style.borderRadius = '12px';
    msg.innerHTML = `${icone} ${mensagem}`;
    bsToast.show();
  }

  // -------------------------------------------------------------------------
  // Utils
  // -------------------------------------------------------------------------
  function escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g,  '&amp;')
      .replace(/</g,  '&lt;')
      .replace(/>/g,  '&gt;')
      .replace(/"/g,  '&quot;')
      .replace(/'/g,  '&#x27;');
  }

  function formatarData(dataStr) {
    if (!dataStr) return '-';
    try {
      const partes = dataStr.split('T')[0].split('-');
      if (partes.length === 3) return `${partes[2]}/${partes[1]}/${partes[0]}`;
      return dataStr;
    } catch { return dataStr; }
  }

  function isoParaInput(dataStr) {
    // Converte "2025-03-15" (ou com T...) para "2025-03-15" (formato de input date)
    if (!dataStr) return '';
    return dataStr.split('T')[0];
  }

  function obterBadgeStatus(status) {
    switch (status) {
      case 'ativo':    return '<span class="badge bg-success">Ativo</span>';
      case 'concluido':return '<span class="badge bg-primary">Concluído</span>';
      case 'suspenso': return '<span class="badge bg-danger">Suspenso</span>';
      default:         return `<span class="badge bg-secondary">${escapeHTML(status)}</span>`;
    }
  }

  function obterTextoPeriodicidade(p) {
    if (!p) return '-';
    const map = { semanal: 'Semanal', quinzenal: 'Quinzenal', mensal: 'Mensal', outra: 'Outra' };
    return map[p] || escapeHTML(p);
  }

  // -------------------------------------------------------------------------
  // Perfil e Autenticação
  // -------------------------------------------------------------------------
  let userUnidadeId = null;

  function preencherPerfil() {
    try {
      const user = JSON.parse(localStorage.getItem('saadi_user_info') || '{}');
      if (user && user.nome) {
        userUnidadeId = user.unidade_id || null;
        if (nomeUsuarioEl)
          nomeUsuarioEl.textContent = `Bem-vindo(a), ${user.nome.split(' ')[0]}!`;
        if (nomeInstituicaoEl && user.unidade_name)
          nomeInstituicaoEl.textContent = user.unidade_name;
      }
    } catch (err) {
      console.error('[SAADI] Erro ao carregar perfil:', err);
    }
  }

  function inicializarSair() {
    if (!btnSair) return;
    btnSair.addEventListener('click', async function (e) {
      e.preventDefault();
      try {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
      } catch (err) {
        console.warn('[SAADI] Erro no logout:', err);
      } finally {
        if (window.saadiAuth?.clearTokens) window.saadiAuth.clearTokens();
        window.location.href = '/index.html';
      }
    });
  }

  // -------------------------------------------------------------------------
  // Datas Padrão
  // -------------------------------------------------------------------------
  function setarDatasPadrao() {
    const hoje = new Date();
    if (inputDataInicio) inputDataInicio.value = hoje.toISOString().split('T')[0];
    if (inputDataFim) {
      const fim = new Date();
      fim.setMonth(hoje.getMonth() + 6);
      inputDataFim.value = fim.toISOString().split('T')[0];
    }
  }

  // -------------------------------------------------------------------------
  // Alunos
  // -------------------------------------------------------------------------
  async function carregarAlunos() {
    if (!selectAluno) return;
    try {
      let url = '/api/alunos?limit=100&status=ativo';
      if (userUnidadeId) url += `&unidade_id=${userUnidadeId}`;
      const resp = await fetch(url, { credentials: 'same-origin', headers: { Accept: 'application/json' } });
      if (!resp.ok) throw new Error(`Status: ${resp.status}`);
      const json   = await resp.json();
      const alunos = json.data?.items || json.items || [];
      selectAluno.innerHTML = '<option value="">Selecione um aluno...</option>';
      alunos.forEach(a => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = `${a.nome_completo} (RA: ${a.ra || '-'})`;
        selectAluno.appendChild(opt);
      });
    } catch (err) {
      console.error('[SAADI] Erro ao carregar alunos:', err);
      selectAluno.innerHTML = '<option value="">Erro ao carregar alunos</option>';
    }
  }

  // -------------------------------------------------------------------------
  // Dashboard
  // -------------------------------------------------------------------------
  async function carregarMétricas() {
    try {
      const resp = await fetch('/api/planos/dashboard', { credentials: 'same-origin', headers: { Accept: 'application/json' } });
      if (!resp.ok) return;
      const json = await resp.json();
      const d    = json.data ?? json;
      if (totalPlanosEl)           totalPlanosEl.textContent           = d.total    ?? '0';
      if (totalPlanosAtivosEl)     totalPlanosAtivosEl.textContent     = d.ativos   ?? '0';
      if (totalPlanosConcluidosEl) totalPlanosConcluidosEl.textContent = d.concluidos?? '0';
      if (totalPlanosSuspensosEl)  totalPlanosSuspensosEl.textContent  = d.suspensos?? '0';
    } catch (err) {
      console.error('[SAADI] Erro ao carregar métricas:', err);
    }
  }

  // -------------------------------------------------------------------------
  // Tabela de Planos
  // -------------------------------------------------------------------------
  async function carregarTabelaPlanos(page = 1) {
    if (!tabelaBody) return;
    tabelaBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Carregando planos...</td></tr>';

    try {
      const resp = await fetch(`/api/planos?page=${page}&limit=${limiteItens}`, {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      });
      if (!resp.ok) throw new Error(`Status: ${resp.status}`);

      const json  = await resp.json();
      const items = json.data?.items || json.items || [];
      const total = json.data?.total  || json.total  || 0;

      if (items.length === 0) {
        tabelaBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Nenhum plano de acompanhamento cadastrado.</td></tr>';
        if (paginacaoEl) paginacaoEl.innerHTML = '';
        return;
      }

      tabelaBody.innerHTML = '';
      items.forEach(p => {
        const tr = document.createElement('tr');
        // Armazenar dados completos no dataset para acesso rápido
        tr.dataset.plano = JSON.stringify(p);

        tr.innerHTML = `
          <td><strong>${escapeHTML(formatarData(p.data_inicio))}</strong></td>
          <td>${escapeHTML(p.aluno_nome)}</td>
          <td>${escapeHTML(p.titulo)}</td>
          <td>
            <div class="text-truncate" style="max-width:260px;" title="${escapeHTML(p.objetivo_geral || '')}">
              ${escapeHTML(p.objetivo_geral || '-')}
            </div>
          </td>
          <td>${obterTextoPeriodicidade(p.periodicidade)}</td>
          <td>${obterBadgeStatus(p.status)}</td>
          <td class="acoes-cell text-center">
            <div class="d-flex gap-2 justify-content-center">
              <button
                class="btn-acao btn-ver"
                data-id="${p.id}"
                data-acao="ver"
                title="Visualizar"
                aria-label="Visualizar plano de ${escapeHTML(p.aluno_nome)}">
                <span aria-hidden="true" style="font-weight:700;font-size:.82rem;letter-spacing:.02em;">V</span>
              </button>
              <button
                class="btn-acao btn-editar"
                data-id="${p.id}"
                data-acao="editar"
                title="Editar"
                aria-label="Editar plano de ${escapeHTML(p.aluno_nome)}">
                <span aria-hidden="true" style="font-weight:700;font-size:.82rem;letter-spacing:.02em;">E</span>
              </button>
              <button
                class="btn-acao btn-deletar"
                data-id="${p.id}"
                data-acao="deletar"
                data-titulo="${escapeHTML(p.titulo)}"
                data-aluno="${escapeHTML(p.aluno_nome)}"
                title="Excluir"
                aria-label="Excluir plano de ${escapeHTML(p.aluno_nome)}">
                <span aria-hidden="true" style="font-weight:700;font-size:.82rem;letter-spacing:.02em;">D</span>
              </button>
            </div>
          </td>
        `;
        tabelaBody.appendChild(tr);
      });

      paginaAtual = page;
      renderizarPaginacao(total);
    } catch (err) {
      console.error('[SAADI] Erro ao listar planos:', err);
      tabelaBody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Falha ao carregar planos de acompanhamento.</td></tr>';
    }
  }

  function renderizarPaginacao(totalItens) {
    if (!paginacaoEl) return;
    const totalPaginas = Math.ceil(totalItens / limiteItens);
    if (totalPaginas <= 1) { paginacaoEl.innerHTML = ''; return; }

    let html = '<ul class="pagination pagination-sm m-0">';
    html += `<li class="page-item ${paginaAtual === 1 ? 'disabled' : ''}">
      <button class="page-link" data-page="${paginaAtual - 1}" type="button">Anterior</button></li>`;
    for (let i = 1; i <= totalPaginas; i++) {
      html += `<li class="page-item ${paginaAtual === i ? 'active' : ''}">
        <button class="page-link" data-page="${i}" type="button">${i}</button></li>`;
    }
    html += `<li class="page-item ${paginaAtual === totalPaginas ? 'disabled' : ''}">
      <button class="page-link" data-page="${paginaAtual + 1}" type="button">Próximo</button></li>`;
    html += '</ul>';
    paginacaoEl.innerHTML = html;

    paginacaoEl.querySelectorAll('.page-link').forEach(btn => {
      btn.addEventListener('click', function () {
        const pg = parseInt(this.dataset.page, 10);
        if (pg && pg !== paginaAtual) carregarTabelaPlanos(pg);
      });
    });
  }

  // -------------------------------------------------------------------------
  // Ações da Tabela (delegação de eventos)
  // -------------------------------------------------------------------------
  function inicializarAcoesTabela() {
    if (!tabelaBody) return;

    tabelaBody.addEventListener('click', async function (e) {
      const btn = e.target.closest('[data-acao]');
      if (!btn) return;

      const acao   = btn.dataset.acao;
      const planoId= parseInt(btn.dataset.id, 10);

      if (acao === 'ver')    await abrirModalVer(planoId, btn);
      if (acao === 'editar') await abrirModalEditar(planoId, btn);
      if (acao === 'deletar')abrirModalDeletar(planoId, btn);
    });
  }

  // ── Buscar plano por ID ───────────────────────────────────────────────────
  async function buscarPlano(planoId) {
    const resp = await fetch(`/api/planos/${planoId}`, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    });
    if (!resp.ok) throw new Error(`Erro ao buscar plano (status ${resp.status})`);
    const json = await resp.json();
    return json.data?.item || json.item || json.data || json;
  }

  // ── MODAL VER ─────────────────────────────────────────────────────────────
  async function abrirModalVer(planoId, btnOrigem) {
    const conteudo = document.getElementById('modalVerConteudo');
    if (!conteudo || !bsModalVer) return;

    conteudo.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Carregando...</p></div>';
    bsModalVer.show();

    try {
      const p = await buscarPlano(planoId);

      conteudo.innerHTML = `
        <div class="row g-3">
          <div class="col-12">
            <div class="d-flex align-items-center gap-2 mb-1">
              <i class="bi bi-person-circle text-primary fs-5"></i>
              <span class="text-muted" style="font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;">Aluno</span>
            </div>
            <p class="fw-bold mb-0" style="color:#0f2744;font-size:1.05rem;">${escapeHTML(p.aluno_nome || '-')}</p>
          </div>

          <div class="col-12"><hr class="my-1" style="border-color:#e8f0fa;"></div>

          <div class="col-md-8">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Título do Plano</label>
            <p class="fw-semibold mb-0" style="color:#0f2744;">${escapeHTML(p.titulo || '-')}</p>
          </div>
          <div class="col-md-4">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Situação</label>
            <div>${obterBadgeStatus(p.status)}</div>
          </div>

          <div class="col-md-4">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Data de Início</label>
            <p class="mb-0 fw-semibold">${escapeHTML(formatarData(p.data_inicio))}</p>
          </div>
          <div class="col-md-4">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Previsão de Fim</label>
            <p class="mb-0">${escapeHTML(formatarData(p.data_fim_prevista))}</p>
          </div>
          <div class="col-md-4">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Periodicidade</label>
            <p class="mb-0">${obterTextoPeriodicidade(p.periodicidade)}</p>
          </div>

          <div class="col-12">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Objetivo Geral</label>
            <div class="p-3 rounded" style="background:#f7faff;border:1px solid #d4e3f5;white-space:pre-wrap;font-size:.92rem;">
              ${escapeHTML(p.objetivo_geral || 'Não informado.')}
            </div>
          </div>

          <div class="col-12">
            <label class="text-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;">Estratégias / Ações</label>
            <div class="p-3 rounded" style="background:#f7faff;border:1px solid #d4e3f5;white-space:pre-wrap;font-size:.92rem;">
              ${escapeHTML(p.estrategias || 'Não informadas.')}
            </div>
          </div>

          <div class="col-12">
            <div class="d-flex gap-3 flex-wrap mt-1">
              <small class="text-muted"><i class="bi bi-calendar3 me-1"></i>Criado em: ${escapeHTML(formatarData(p.created_at))}</small>
              <small class="text-muted"><i class="bi bi-clock-history me-1"></i>Atualizado em: ${escapeHTML(formatarData(p.updated_at))}</small>
            </div>
          </div>
        </div>`;
    } catch (err) {
      conteudo.innerHTML = `<div class="alert alert-danger">Erro ao carregar dados do plano: ${escapeHTML(err.message)}</div>`;
    }
  }

  // ── MODAL EDITAR ──────────────────────────────────────────────────────────
  async function abrirModalEditar(planoId, btnOrigem) {
    if (!bsModalEditar) return;

    // Limpar e mostrar spinner enquanto carrega
    document.getElementById('editTitulo').value       = '';
    document.getElementById('editObjetivo').value     = '';
    document.getElementById('editEstrategias').value  = '';
    document.getElementById('editDataInicio').value   = '';
    document.getElementById('editDataFim').value      = '';
    document.getElementById('editPlanoId').value      = planoId;
    bsModalEditar.show();

    try {
      const p = await buscarPlano(planoId);
      document.getElementById('editTitulo').value      = p.titulo        || '';
      document.getElementById('editObjetivo').value    = p.objetivo_geral|| '';
      document.getElementById('editEstrategias').value = p.estrategias   || '';
      document.getElementById('editDataInicio').value  = isoParaInput(p.data_inicio);
      document.getElementById('editDataFim').value     = isoParaInput(p.data_fim_prevista);

      const selPer = document.getElementById('editPeriodicidade');
      const selSt  = document.getElementById('editStatus');
      if (selPer) selPer.value = p.periodicidade || 'semanal';
      if (selSt)  selSt.value  = p.status        || 'ativo';
    } catch (err) {
      exibirToast(`Erro ao carregar plano: ${err.message}`, 'error');
      bsModalEditar.hide();
    }
  }

  function inicializarBotaoSalvarEdicao() {
    const btn = document.getElementById('btnSalvarEdicao');
    const spinner = document.getElementById('spinnerEdicao');
    if (!btn) return;

    btn.addEventListener('click', async () => {
      const planoId = parseInt(document.getElementById('editPlanoId').value, 10);
      const titulo  = document.getElementById('editTitulo').value.trim();
      if (!titulo) {
        exibirToast('O título do plano é obrigatório.', 'error');
        return;
      }

      const payload = {
        titulo,
        objetivo_geral : document.getElementById('editObjetivo').value.trim()    || null,
        estrategias    : document.getElementById('editEstrategias').value.trim()  || null,
        periodicidade  : document.getElementById('editPeriodicidade').value,
        status         : document.getElementById('editStatus').value,
        data_inicio    : document.getElementById('editDataInicio').value           || null,
        data_fim_prevista: document.getElementById('editDataFim').value            || null,
      };

      btn.disabled = true;
      spinner.classList.remove('d-none');

      try {
        const resp = await fetch(`/api/planos/${planoId}`, {
          method: 'PUT',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.message || 'Erro ao salvar alterações.');
        }

        bsModalEditar.hide();
        exibirToast('Plano atualizado com sucesso!', 'success');
        await Promise.all([carregarMétricas(), carregarTabelaPlanos(paginaAtual)]);
      } catch (err) {
        exibirToast(`Erro: ${err.message}`, 'error');
      } finally {
        btn.disabled = false;
        spinner.classList.add('d-none');
      }
    });
  }

  // ── MODAL DELETAR ─────────────────────────────────────────────────────────
  let planoIdParaDeletar = null;

  function abrirModalDeletar(planoId, btn) {
    if (!bsModalDeletar) return;
    planoIdParaDeletar = planoId;

    const titulo = btn.dataset.titulo || 'este plano';
    const aluno  = btn.dataset.aluno  || '';
    const labelEl= document.getElementById('modalDeletarNomePlano');
    if (labelEl) labelEl.textContent = `"${titulo}" — ${aluno}`;

    bsModalDeletar.show();
  }

  function inicializarBotaoConfirmarExclusao() {
    const btn     = document.getElementById('btnConfirmarExclusao');
    const spinner = document.getElementById('spinnerDelecao');
    if (!btn) return;

    btn.addEventListener('click', async () => {
      if (!planoIdParaDeletar) return;
      btn.disabled = true;
      spinner.classList.remove('d-none');

      try {
        const resp = await fetch(`/api/planos/${planoIdParaDeletar}`, {
          method: 'DELETE',
          credentials: 'same-origin',
          headers: { Accept: 'application/json' },
        });
        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.message || 'Erro ao excluir plano.');
        }

        bsModalDeletar.hide();
        exibirToast('Plano excluído com sucesso!', 'success');
        planoIdParaDeletar = null;
        await Promise.all([carregarMétricas(), carregarTabelaPlanos(paginaAtual)]);
      } catch (err) {
        exibirToast(`Erro: ${err.message}`, 'error');
      } finally {
        btn.disabled = false;
        spinner.classList.add('d-none');
      }
    });
  }

  // -------------------------------------------------------------------------
  // Formulário de criação
  // -------------------------------------------------------------------------
  function inicializarFormulario() {
    if (!formPlano) return;
    formPlano.addEventListener('submit', async function (e) {
      e.preventDefault();

      const alunoId     = parseInt(selectAluno.value, 10);
      const titulo      = inputTitulo.value.trim();
      const dataInicio  = inputDataInicio.value;
      const dataFim     = inputDataFim.value;
      const periodicidade = selectPeriodicidade.value;
      const status      = selectStatus.value;
      const objetivo    = textObjetivo.value.trim();
      const estrategias = textEstrategias.value.trim();

      if (!alunoId) { alert('Por favor, selecione um estudante.'); return; }
      if (!titulo)  { alert('Por favor, preencha o título do plano.'); return; }

      const payload = {
        aluno_id: alunoId,
        titulo,
        data_inicio: dataInicio || null,
        data_fim_prevista: dataFim || null,
        periodicidade,
        status,
        objetivo_geral: objetivo   || null,
        estrategias:    estrategias|| null,
      };

      const submitBtn = formPlano.querySelector('button[type="submit"]');
      try {
        if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Gravando...'; }

        const resp = await fetch('/api/planos', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.message || 'Erro ao criar plano.');
        }

        exibirToast('Plano cadastrado com sucesso!', 'success');
        formPlano.reset();
        setarDatasPadrao();
        await Promise.all([carregarMétricas(), carregarTabelaPlanos(1)]);
      } catch (err) {
        exibirToast(`Erro: ${err.message}`, 'error');
      } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Salvar plano'; }
      }
    });
  }

  // -------------------------------------------------------------------------
  // Filtros
  // -------------------------------------------------------------------------
  function aplicarFiltros() {
    const termoBusca = (document.getElementById('filtroBuscaAluno')?.value || '').toLowerCase();
    const status     = (document.getElementById('filtroStatus')?.value || '').toLowerCase();
    const frequencia = (document.getElementById('filtroFrequencia')?.value || '').toLowerCase();

    document.querySelectorAll('#tabelaPlanos tbody tr').forEach(linha => {
      const primeiraCelula = linha.querySelector('td');
      if (primeiraCelula && primeiraCelula.colSpan >= 6) return;

      const nomeAluno   = linha.children[1]?.textContent.toLowerCase() || '';
      const periodicidade= linha.children[4]?.textContent.toLowerCase() || '';
      const badgeStatus = linha.children[5]?.textContent.toLowerCase() || '';

      let mostrar = true;
      if (termoBusca && !nomeAluno.includes(termoBusca)) mostrar = false;
      if (status) {
        if (status === 'ativo'     && !badgeStatus.includes('ativo'))     mostrar = false;
        if (status === 'concluido' && !badgeStatus.includes('concluído')) mostrar = false;
        if (status === 'suspenso'  && !badgeStatus.includes('suspenso'))  mostrar = false;
      }
      if (frequencia && !periodicidade.includes(frequencia)) mostrar = false;

      linha.style.display    = mostrar ? '' : 'none';
      linha.style.transition = 'opacity 0.3s ease';
      linha.style.opacity    = mostrar ? '1' : '0';
    });
  }

  function inicializarFiltros() {
    const formFiltros = document.getElementById('formFiltrosPlanos');
    if (!formFiltros) return;
    formFiltros.addEventListener('submit', (e) => { e.preventDefault(); aplicarFiltros(); });
    document.getElementById('btnLimparFiltros')?.addEventListener('click', () => { formFiltros.reset(); aplicarFiltros(); });
    document.getElementById('filtroBuscaAluno')?.addEventListener('input', aplicarFiltros);
    document.getElementById('filtroStatus')?.addEventListener('change', aplicarFiltros);
    document.getElementById('filtroResponsavel')?.addEventListener('change', aplicarFiltros);
    document.getElementById('filtroFrequencia')?.addEventListener('change', aplicarFiltros);
  }

  // -------------------------------------------------------------------------
  // Inicialização Geral
  // -------------------------------------------------------------------------
  function init() {
    preencherPerfil();
    inicializarSair();
    setarDatasPadrao();
    inicializarModais();
    carregarAlunos();
    carregarMétricas();
    carregarTabelaPlanos(1);
    inicializarFormulario();
    inicializarFiltros();
    inicializarAcoesTabela();
    inicializarBotaoSalvarEdicao();
    inicializarBotaoConfirmarExclusao();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
