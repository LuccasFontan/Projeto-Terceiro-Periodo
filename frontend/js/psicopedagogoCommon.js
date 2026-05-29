/**
 * psicopedagogoCommon.js
 * Funcionalidades comuns para as páginas do Psicopedagogo.
 * Preenche o perfil e inicializa o botão de sair.
 */
(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // Perfil e Autenticação
  // -------------------------------------------------------------------------
  function preencherPerfil() {
    try {
      const user = JSON.parse(localStorage.getItem('saadi_user_info') || '{}');
      const nomeUsuarioEl = document.getElementById('nomeUsuario');
      const emailPerfilEl = document.querySelector('.emailPerfil');
      const nomeInstituicaoEl = document.getElementById('nomeInstituicao');
      
      if (user && user.nome) {
        if (nomeUsuarioEl) {
          nomeUsuarioEl.textContent = `Olá, ${user.nome.split(' ')[0]}`;
        }
        if (emailPerfilEl && user.email) {
          emailPerfilEl.textContent = user.email;
        }
        if (nomeInstituicaoEl && user.unidade_nome) {
          nomeInstituicaoEl.textContent = user.unidade_nome;
        } else if (nomeInstituicaoEl) {
          nomeInstituicaoEl.textContent = 'Unidade Escolar Geral';
        }
      }
    } catch (err) {
      console.error('[SAADI] Erro ao carregar informações de perfil:', err);
    }
  }

  function inicializarSair() {
    const btnSair = document.getElementById('btnSair');
    const linksSair = document.querySelectorAll('a.textoSair, a[href*="login.html"]');

    const logoutFunc = async function (e) {
      e.preventDefault();
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          credentials: 'same-origin',
        });
      } catch (err) {
        console.warn('[SAADI] Erro ao chamar endpoint de logout:', err);
      } finally {
        if (window.saadiAuth && typeof window.saadiAuth.clearTokens === 'function') {
          window.saadiAuth.clearTokens();
        }
        window.location.href = '/index.html';
      }
    };

    if (btnSair) {
      btnSair.removeEventListener('click', logoutFunc);
      btnSair.addEventListener('click', logoutFunc);
    }
    
    linksSair.forEach(link => {
        link.removeEventListener('click', logoutFunc);
        link.addEventListener('click', logoutFunc);
    });
  }

  // -------------------------------------------------------------------------
  // Modal de Configurações
  // -------------------------------------------------------------------------
  function inicializarConfiguracoes() {
    // 1. Injetar o Modal no DOM caso não exista
    if (!document.getElementById('modalConfiguracoesUsuario')) {
      const modalHtml = `
        <div class="modal fade" id="modalConfiguracoesUsuario" tabindex="-1" aria-labelledby="modalConfiguracoesUsuarioTitulo" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content modalConfigSecretaria">
                    <div class="modal-header modalConfigCabecalho" style="background: linear-gradient(135deg, var(--psico-900) 0%, var(--psico-700) 100%); color: #fff;">
                        <h2 class="modal-title fs-5" id="modalConfiguracoesUsuarioTitulo">Configurações do Usuário</h2>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Fechar"></button>
                    </div>
                    <form class="modalConfigCorpo" id="formConfiguracoesUsuario">
                        <div class="modal-body">
                            <p class="modalConfigDescricao text-muted">Atualize suas preferências e dados de perfil.</p>
                            <div class="mb-3">
                                <label for="nomeExibicao" class="form-label">Nome completo</label>
                                <input type="text" class="form-control" id="nomeExibicao" name="nome_completo" required>
                            </div>
                            <div class="mb-3">
                                <label for="emailInstitucional" class="form-label">E-mail</label>
                                <input type="email" class="form-control" id="emailInstitucional" name="email" readonly>
                            </div>
                            <div class="mb-3">
                                <label for="cpfUsuario" class="form-label">CPF</label>
                                <input type="text" class="form-control" id="cpfUsuario" name="cpf" readonly disabled style="background-color: #e9ecef; cursor: not-allowed;">
                            </div>
                            <div class="mb-3">
                                <label for="novaSenha" class="form-label">Nova Senha (deixe em branco para não alterar)</label>
                                <input type="password" class="form-control" id="novaSenha" name="senha" placeholder="********">
                            </div>
                            <div class="mb-3">
                                <label for="confirmarNovaSenha" class="form-label">Confirmar Nova Senha</label>
                                <input type="password" class="form-control" id="confirmarNovaSenha" placeholder="********">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary" style="background: linear-gradient(135deg, var(--psico-900) 0%, var(--psico-700) 100%); border: none;">Salvar alterações</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
      `;
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = modalHtml;
      document.body.appendChild(tempDiv.firstElementChild);
    }

    // 2. Adicionar atributos data-bs-toggle nos botões de engrenagem
    const btnConfigs = document.querySelectorAll('.config button, button[aria-label="Abrir configurações"]');
    btnConfigs.forEach(btn => {
      btn.setAttribute('data-bs-toggle', 'modal');
      btn.setAttribute('data-bs-target', '#modalConfiguracoesUsuario');
      
      btn.addEventListener('click', () => {
        // Preencher form com dados locais
        const user = JSON.parse(localStorage.getItem('saadi_user_info') || '{}');
        document.getElementById('nomeExibicao').value = user.nome || user.user_name || '';
        document.getElementById('emailInstitucional').value = user.email || '';
        document.getElementById('cpfUsuario').value = user.cpf || '';
        document.getElementById('novaSenha').value = '';
        document.getElementById('confirmarNovaSenha').value = '';
      });
    });

    // 3. Listener do Form
    const form = document.getElementById('formConfiguracoesUsuario');
    if (form && !form.dataset.ready) {
      form.dataset.ready = 'true';
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const novaSenha = form.querySelector('#novaSenha').value;
        const confirmarSenha = form.querySelector('#confirmarNovaSenha').value;
        
        if (novaSenha && novaSenha !== confirmarSenha) {
          alert('As senhas não coincidem. Por favor, verifique.');
          return;
        }

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = 'Salvando...';
        btn.disabled = true;

        const payload = {
          nome_completo: form.querySelector('#nomeExibicao').value.trim(),
        };

        if (novaSenha) payload.senha = novaSenha;

        try {
          const fetchMethod = window.saadiApiFetch || window.fetch;
          const resp = await fetchMethod('/api/auth/me', {
            method: 'PUT',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
          });

          if (resp.ok) {
            alert('Perfil atualizado com sucesso!');
            // Atualizar localStorage para refletir mudança instantânea localmente
            const user = JSON.parse(localStorage.getItem('saadi_user_info') || '{}');
            user.nome = payload.nome_completo;
            localStorage.setItem('saadi_user_info', JSON.stringify(user));
            
            preencherPerfil();
            
            if (window.bootstrap) {
              const modalEl = document.getElementById('modalConfiguracoesUsuario');
              const bsModal = bootstrap.Modal.getInstance(modalEl);
              if (bsModal) bsModal.hide();
            }
          } else {
            const erro = await resp.json().catch(() => ({}));
            alert(erro.message || 'Erro ao atualizar perfil.');
          }
        } catch (err) {
          console.error('[SAADI] Erro ao salvar perfil:', err);
          alert('Erro de conexão.');
        } finally {
          btn.textContent = originalText;
          btn.disabled = false;
        }
      });
    }
  }

  // -------------------------------------------------------------------------
  // Inicialização
  // -------------------------------------------------------------------------
  function init() {
    preencherPerfil();
    inicializarSair();
    inicializarConfiguracoes();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
