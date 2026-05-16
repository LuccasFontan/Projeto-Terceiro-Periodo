# Integração Frontend + Backend

Este guia mostra como ligar o frontend HTML/JS ao backend Flask utilizando autenticação segura com **Cookies HttpOnly**.
*Aviso: Nunca manipule tokens diretamente via `localStorage`. Eles são automaticamente gerenciados pelo navegador via cookies.*

## 1. Login

O endpoint retorna as informações do usuário logado em `data.user`. O navegador salvará os cookies automaticamente.

```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    email: document.getElementById('email').value,
    senha: document.getElementById('senha').value
  })
});

const data = await response.json();

if (!response.ok) {
  throw new Error(data.message || 'Falha no login');
}

// Salva apenas informações não-sensíveis para UX (ex: exibir o nome na tela)
if (data.user) {
    localStorage.setItem('saadi_user_info', JSON.stringify(data.user));
}

// O token não está mais na resposta JSON (data.access_token). O Backend injetou o HttpOnly Cookie!
window.location.href = data.redirect_url;
```

## 2. Realizando Requisições Autenticadas (Listagem/Cadastro)

**Regra de Ouro:** Todas as chamadas para `/api/*` devem incluir `credentials: 'same-origin'` no fetch para o navegador anexar os cookies HttpOnly.
Você **NÃO** precisa mais enviar o header `Authorization: Bearer <token>`.

```javascript
// Exemplo: Listagem
const response = await fetch('/api/admin/usuarios?page=1&limit=20', {
  method: 'GET',
  credentials: 'same-origin', // <--- OBRIGATÓRIO PARA ENVIAR O COOKIE
  headers: {
    'Accept': 'application/json'
  }
});

const data = await response.json();
console.log(data.items);
```

## 3. Cadastro com POST

```javascript
const response = await fetch('/api/admin/unidades', {
  method: 'POST',
  credentials: 'same-origin', // <--- OBRIGATÓRIO PARA ENVIAR O COOKIE
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    nome: 'Escola Municipal Centro',
    sigla: 'EMC',
    cnpj: '00.000.000/0001-00',
    email: 'contato@escola.edu.br'
  })
});

const data = await response.json();
```

## 4. Uso Global (Recomendado)

Para evitar repetir `credentials: 'same-origin'` em cada requisição, recomendamos importar o script global `apiClient.js` nas suas páginas HTML:

```html
<script src="/scripts/apiClient.js"></script>
```

Ele irá sobrescrever o `fetch` nativo e **injetar automaticamente** as credenciais e tratar a renovação de sessão (`/api/auth/refresh`) nos bastidores. 
Assim, você poderá fazer os `fetch('/api/...')` normalmente em sua página.

## 5. Logout

```javascript
await fetch('/api/auth/logout', {
  method: 'POST',
  credentials: 'same-origin',
  headers: {
    'Accept': 'application/json'
  }
});

// Limpa dados de UX
localStorage.removeItem('saadi_user_info');
window.location.href = '/index.html';
```
