# 📋 Checklist de Preparação - SAADI Backend Ready

## ✅ O que foi feito

### Painel Principal do Administrador
- [x] Removidos dados fictícios
- [x] Estrutura HTML preparada com IDs dinâmicos
- [x] JavaScript implementado para carregar dados da API
- [x] Endpoints especificados (dashboard, atividades, status)
- [x] Exemplo de implementação Flask fornecido

### Documentação
- [x] `BACKEND_API_SPEC.md` - Especificação completa de endpoints
- [x] `BACKEND_IMPLEMENTATION_EXAMPLE.md` - Exemplo de implementação

---

## 🔄 Próximas Páginas do Administrador para Preparação

### 1. **Página de Usuários** (listarUsuarios.html)
   - [ ] Verificar se dados fictícios foram removidos
   - [ ] Verificar IDs dos elementos
   - [ ] JavaScript já implementado? SIM (verificar)
   - Endpoints para implementar:
     - `GET /api/admin/usuarios` - Listar usuários
     - `GET /api/admin/unidades` - Para populate filtros
     - `DELETE /api/admin/usuarios/{id}` - Deletar
     - `GET /api/admin/usuarios/{id}` - Obter detalhes

### 2. **Página de Unidades** (listarUnidades.html)
   - [ ] Remover dados fictícios
   - [ ] Adicionar IDs aos elementos
   - [ ] Implementar JavaScript dinâmico
   - Endpoints para implementar:
     - `GET /api/admin/unidades` - Listar unidades
     - `DELETE /api/admin/unidades/{id}` - Deletar
     - `GET /api/admin/unidades/{id}` - Obter detalhes

### 3. **Página de Relatórios** (relatoriosAdministrador.html)
   - [ ] Remover dados fictícios
   - [ ] Adicionar IDs aos gráficos (canvas)
   - [ ] Implementar carregamento de gráficos via Chart.js
   - Endpoints para implementar:
     - `GET /api/admin/relatorios/dashboard` - Dados dos gráficos

### 4. **Página de Auditoria** (auditoria.html)
   - [ ] Remover dados fictícios
   - [ ] Adicionar IDs aos elementos
   - [ ] Implementar paginação
   - Endpoints para implementar:
     - `GET /api/admin/auditoria` - Listar atividades

### 5. **Página de Parâmetros** (parametros.html)
   - [ ] Remover valores padrão de formulários
   - [ ] Implementar carregamento e salvamento de configurações
   - Endpoints para implementar:
     - `GET /api/admin/parametros` - Obter parâmetros
     - `PUT /api/admin/parametros` - Atualizar parâmetros

### 6. **Página de Alunos Central** (alunos/listarAlunos.html)
   - [ ] Remover dados fictícios
   - [ ] Adicionar IDs aos elementos
   - [ ] Implementar filtros dinâmicos
   - Endpoints para implementar:
     - `GET /api/admin/alunos` - Listar alunos

---

## 🛠️ Páginas de Cadastro/Atualização para Preparação

### Formulários de Usuários
- [x] atualizarUsuarios.html - Dados fictícios removidos
- [x] cadastroUsuarios.html - Dados fictícios removidos
- [ ] Implementar carregamento de dados (GET)
- [ ] Implementar envio de dados (POST/PUT)
- [ ] Implementar validação no frontend

### Formulários de Unidades
- [x] atualizarUnidades.html - Dados fictícios removidos
- [x] cadastroUnidades.html - Dados fictícios removidos
- [ ] Implementar carregamento de dados (GET)
- [ ] Implementar envio de dados (POST/PUT)

---

## 🚀 Passos para Completar a Preparação

### Fase 1: Preparação do Frontend (Esta semana)
1. [ ] Verificar `listarUsuarios.html` se já foi desfeito
2. [ ] Preparar `listarUnidades.html`
3. [ ] Preparar `relatoriosAdministrador.html`
4. [ ] Preparar `auditoria.html`
5. [ ] Preparar `parametros.html`
6. [ ] Preparar páginas de cadastro/atualização

### Fase 2: Preparação do Backend (Próxima semana)
1. [ ] Criar estrutura de diretórios Flask
2. [ ] Implementar modelos de dados (SQLAlchemy)
3. [ ] Implementar autenticação JWT
4. [ ] Implementar endpoints do dashboard
5. [ ] Implementar endpoints de usuários
6. [ ] Implementar endpoints de unidades
7. [ ] Testar endpoints com Postman

### Fase 3: Integração (Após backend pronto)
1. [ ] Conectar frontend ao backend
2. [ ] Testar fluxos completos
3. [ ] Corrigir bugs
4. [ ] Otimizar performance

---

## 📝 Estrutura de Arquivos

```
projeto/
├── pages/
│   ├── auth/
│   │   ├── login.html
│   │   └── redefinirSenha.html
│   └── menus/
│       ├── administrador/
│       │   ├── menuAdministrador.html ✅ PRONTO
│       │   ├── usuarios/
│       │   │   ├── listarUsuarios.html (⚠️ em revisão)
│       │   │   ├── cadastroUsuarios.html ✅
│       │   │   ├── atualizarUsuarios.html ✅
│       │   │   └── deletarUsuarios.html
│       │   ├── unidades/
│       │   │   ├── listarUnidades.html (⏳ próximo)
│       │   │   ├── cadastroUnidades.html ✅
│       │   │   ├── atualizarUnidades.html ✅
│       │   │   └── deletarUnidades.html
│       │   ├── alunos/
│       │   │   └── listarAlunos.html (⏳ próximo)
│       │   ├── relatoriosAdministrador.html (⏳ próximo)
│       │   ├── auditoria.html (⏳ próximo)
│       │   ├── parametros.html (⏳ próximo)
│       │   └── perfis/
│       │       └── vinculacaoPerfis.html
│       ├── psicopedagogo/
│       └── secretaria/
│
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── decorators.py
│   └── routes/
│       ├── admin_dashboard.py 📝 (exemplo criado)
│       ├── admin_usuarios.py 📝 (exemplo criado)
│       ├── admin_unidades.py
│       ├── admin_relatorios.py
│       └── ...
│
├── BACKEND_API_SPEC.md ✅
├── BACKEND_IMPLEMENTATION_EXAMPLE.md ✅
├── SETUP_PREPARACAO.md (este arquivo)
└── app.py
```

---

## 🔑 Endpoints Essenciais a Implementar

### Dashboard
```
GET /api/admin/dashboard
GET /api/admin/atividades-recentes
GET /api/admin/status-sistema
```

### Usuários
```
GET /api/admin/usuarios
GET /api/admin/usuarios/{id}
POST /api/admin/usuarios
PUT /api/admin/usuarios/{id}
DELETE /api/admin/usuarios/{id}
```

### Unidades
```
GET /api/admin/unidades
GET /api/admin/unidades/{id}
POST /api/admin/unidades
PUT /api/admin/unidades/{id}
DELETE /api/admin/unidades/{id}
```

### Outros
```
GET /api/admin/alunos
GET /api/admin/relatorios/dashboard
GET /api/admin/auditoria
GET /api/admin/parametros
PUT /api/admin/parametros
POST /api/auth/logout
```

---

## 📚 Referências de Implementação

- `BACKEND_API_SPEC.md` - Especificação completa
- `BACKEND_IMPLEMENTATION_EXAMPLE.md` - Código exemplo
- Modelos já criados em `backend/models.py`
- Rotas base em `backend/routes/`

---

## ✨ Status Atual: PRONTO PARA BACKEND

O painel principal foi **preparado com sucesso** para integração com o backend.

**Próximo passo:** Preparar as outras páginas do administrador seguindo o mesmo padrão do painel principal.

---

**Data de Conclusão:** 10/04/2026
**Status:** ✅ FASE 1 INICIADA - Painel Principal Concluído
