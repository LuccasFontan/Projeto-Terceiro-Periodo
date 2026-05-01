(() => {
  const nativeFetch = window.fetch.bind(window);
  const ACCESS_TOKEN_KEY = 'saadi_access_token';
  const REFRESH_TOKEN_KEY = 'saadi_refresh_token';
  const LOGIN_PATH = '/index.html';
  const REFRESH_ENDPOINT = '/api/auth/refresh';

  function getAccessToken() {
    return null; // Token agora esta em HttpOnly cookie
  }

  function getRefreshToken() {
    return null; // Token agora esta em HttpOnly cookie
  }

  function setTokens(data) {
    if (data.user) {
      localStorage.setItem('saadi_user_info', JSON.stringify(data.user));
    }
  }

  function clearTokens() {
    localStorage.removeItem('saadi_user_info');
  }

  async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    const response = await nativeFetch(REFRESH_ENDPOINT, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      clearTokens();
      return false;
    }

    const data = await response.json().catch(() => ({}));
    setTokens(data);
    return true;
  }

  function shouldAttachAuth(url, options) {
    const method = String(options?.method || 'GET').toUpperCase();
    if (method === 'OPTIONS') {
      return false;
    }

    if (typeof url === 'string' && url.startsWith('/api/auth/login')) {
      return false;
    }

    return true;
  }

  function decodeJwtPayload(token) {
    // Como usamos HttpOnly cookies, o JS nao consegue ler o token.
    // Usamos o localStorage do user info.
    try {
        const user = JSON.parse(localStorage.getItem('saadi_user_info'));
        return user || null;
    } catch {
        return null;
    }
  }

  function firstName(fullName) {
    const text = String(fullName || '').trim();
    if (!text) return '';
    return text.split(' ')[0];
  }

  function renderProfile(profile = {}) {
    const nameEl = document.querySelector('.nomePerfil');
    const metaEl = document.querySelector('.emailPerfil');
    if (!nameEl || !metaEl) return;

    const fName = firstName(profile.nome || profile.user_name);
    nameEl.textContent = fName ? `Olá, ${fName}` : 'Olá';

    const metaParts = [profile.email, profile.perfil || profile.profile_name].filter(Boolean);
    metaEl.textContent = metaParts.length ? metaParts.join(' • ') : 'Sessão ativa';
  }

  async function hydrateProfile() {
    let claims = decodeJwtPayload() || {};
    renderProfile({
      nome: claims.nome,
      email: claims.email,
      perfil: claims.perfil,
    });

    try {
      let response = await nativeFetch('/api/auth/me', {
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json',
        },
      });

      if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          claims = decodeJwtPayload() || claims;
          response = await nativeFetch('/api/auth/me', {
            credentials: 'same-origin',
            headers: {
              Accept: 'application/json',
            },
          });
        }
      }

      if (!response.ok) return;
      const data = await response.json().catch(() => ({}));
      const source = data.data || data;

      renderProfile({
        nome: source.user_name || claims.nome,
        email: claims.email,
        perfil: source.profile_name || claims.perfil,
      });
    } catch {
      // fallback do token ja foi aplicado
    }
  }

  async function apiFetch(url, options = {}) {
    const requestOptions = {
      ...options,
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
        ...(options.headers || {}),
      },
    };

    let response = await nativeFetch(url, requestOptions);

    if (response.status !== 401 || !shouldAttachAuth(url, requestOptions)) {
      return response;
    }

    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      clearTokens();
      window.location.href = LOGIN_PATH;
      return response;
    }

    const retryOptions = {
      ...requestOptions,
      credentials: 'same-origin',
    };

    response = await nativeFetch(url, retryOptions);
    if (response.status === 401) {
      clearTokens();
      window.location.href = LOGIN_PATH;
    }

    return response;
  }

  window.saadiAuth = {
    getAccessToken,
    getRefreshToken,
    setTokens,
    clearTokens,
    refreshAccessToken,
    hydrateProfile,
  };

  window.saadiApiFetch = apiFetch;
  window.fetch = apiFetch;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hydrateProfile);
  } else {
    hydrateProfile();
  }
})();
