/**
 * menuPsicopedagogo.js
 * Controlador do menu inicial/dashboard do Psicopedagogo.
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // Elementos DOM
  // -------------------------------------------------------------------------
  const totalCasosEl = document.getElementById('totalCasos');
  const totalTriagensEl = document.getElementById('totalTriagens');
  const totalPlanosEl = document.getElementById('totalPlanos');
  const totalAtendimentosEl = document.getElementById('totalAtendimentos');
  const totalEncaminhamentosEl = document.getElementById('totalEncaminhamentos');

  // -------------------------------------------------------------------------
  // Métricas do Dashboard
  // -------------------------------------------------------------------------
  async function carregarDashboard() {
    try {
      const resp = await fetch('/api/psicopedagogo/dashboard', {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      });

      if (!resp.ok) {
        console.warn('[SAADI] Dashboard psicopedagógico indisponível:', resp.status);
        return;
      }

      const json = await resp.json();
      const d = json.data ?? json;

      // Atualiza os contadores no DOM com fallback seguro
      if (totalCasosEl) totalCasosEl.textContent = d.casos_ativos ?? '0';
      if (totalTriagensEl) totalTriagensEl.textContent = d.triagens_pendentes ?? '0';
      if (totalPlanosEl) totalPlanosEl.textContent = d.planos_ativos ?? '0';
      if (totalAtendimentosEl) totalAtendimentosEl.textContent = d.atendimentos_hoje ?? '0';
      if (totalEncaminhamentosEl) totalEncaminhamentosEl.textContent = d.encaminhamentos_abertos ?? '0';

    } catch (err) {
      console.error('[SAADI] Erro ao carregar métricas do dashboard:', err);
    }
  }

  // -------------------------------------------------------------------------
  // Inicialização
  // -------------------------------------------------------------------------
  function init() {
    carregarDashboard();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
