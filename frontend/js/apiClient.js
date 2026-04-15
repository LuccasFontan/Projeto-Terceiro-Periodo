(() => {
  const nativeFetch = window.fetch.bind(window);
  const ACCESS_TOKEN_KEY = 'saadi_access_token';
  const REFRESH_TOKEN_KEY = 'saadi_refresh_token';
  const LOGIN_PATH = '/index.html';
  const REFRESH_ENDPOINT = '/api/auth/refresh';

  function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY) || '';
  }

  function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || '';
  }

  function setTokens(data) {
    if (data.access_token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    }

    if (data.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    }
  }

  function clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    const response = await nativeFetch(REFRESH_ENDPOINT, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${refreshToken}`,
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
    if (!token) return null;
    try {
      const payloadBase64 = token.split('.')[1];
      if (!payloadBase64) return null;
      const base64Url = payloadBase64.replace(/-/g, '+').replace(/_/g, '/');
      const padding = '='.repeat((4 - (base64Url.length % 4)) % 4);
      const base64 = base64Url + padding;
      const json = atob(base64);
      return JSON.parse(json);
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
    let token = getAccessToken();
    if (!token) return;

    let claims = decodeJwtPayload(token) || {};
    renderProfile({
      nome: claims.nome,
      email: claims.email,
      perfil: claims.perfil,
    });

    try {
      let response = await nativeFetch('/api/auth/me', {
        headers: {
          Accept: 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          token = getAccessToken();
          claims = decodeJwtPayload(token) || claims;
          response = await nativeFetch('/api/auth/me', {
            headers: {
              Accept: 'application/json',
              Authorization: `Bearer ${token}`,
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
      headers: {
        Accept: 'application/json',
        ...(options.headers || {}),
      },
    };

    if (shouldAttachAuth(url, requestOptions)) {
      const accessToken = getAccessToken();
      if (accessToken) {
        requestOptions.headers.Authorization = `Bearer ${accessToken}`;
      }
    }

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
      headers: {
        ...requestOptions.headers,
        Authorization: `Bearer ${getAccessToken()}`,
      },
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
