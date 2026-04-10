# Integração Frontend + Backend

Este guia mostra como ligar o frontend HTML/JS puro ao backend Flask com JWT.

## 1. Login

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

localStorage.setItem('saadi_access_token', data.access_token);
localStorage.setItem('saadi_refresh_token', data.refresh_token);
window.location.href = data.redirect_url;
```

## 2. Listagem de dados

```javascript
const token = localStorage.getItem('saadi_access_token');

const response = await fetch('/api/admin/usuarios?page=1&limit=20', {
  headers: {
    'Accept': 'application/json',
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
console.log(data.items);
```

## 3. Cadastro

```javascript
const token = localStorage.getItem('saadi_access_token');

const response = await fetch('/api/admin/unidades', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': `Bearer ${token}`
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

## 4. Envio de formulário HTML

```javascript
document.getElementById('meuFormulario').addEventListener('submit', async (event) => {
  event.preventDefault();

  const token = localStorage.getItem('saadi_access_token');
  const formData = new FormData(event.target);

  const response = await fetch('/api/admin/usuarios', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(Object.fromEntries(formData.entries()))
  });

  const data = await response.json();
  if (!response.ok) {
    alert(data.message || 'Erro ao salvar');
    return;
  }

  alert('Salvo com sucesso');
});
```

## 5. Logout

```javascript
const token = localStorage.getItem('saadi_access_token');

await fetch('/api/auth/logout', {
  method: 'POST',
  headers: {
    'Accept': 'application/json',
    'Authorization': `Bearer ${token}`
  }
});

localStorage.removeItem('saadi_access_token');
localStorage.removeItem('saadi_refresh_token');
window.location.href = '/index.html';
```
