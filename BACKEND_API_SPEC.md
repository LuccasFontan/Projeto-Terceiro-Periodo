# Especificação de Endpoints da API - SAADI

## 📋 Documentação da API Backend

Este documento descreve os endpoints que o backend deve implementar para integração com o frontend do sistema SAADI.

---

## 🎯 Painel Principal - Administrador

### 1. **Endpoint: GET /api/admin/dashboard**

**Descrição:** Retorna as estatísticas principais do painel do administrador.

**Método:** GET

**Autenticação:** Requerida (header Authorization)

**Resposta de Sucesso (200):**
```json
{
  "totalUnidades": 12,
  "usuariosAtivos": 47,
  "configuracoesPendentes": 8,
  "alertaSeguranca": 3
}
```

**Resposta de Erro (4xx/5xx):**
```json
{
  "message": "Erro ao carregar dados do dashboard"
}
```

---

### 2. **Endpoint: GET /api/admin/atividades-recentes**

**Descrição:** Retorna as últimas atividades realizadas no sistema.

**Método:** GET

**Autenticação:** Requerida (header Authorization)

**Query Parameters:**
- `limite` (opcional): número máximo de registros (padrão: 5)
- `offset` (opcional): paginação (padrão: 0)

**Resposta de Sucesso (200):**
```json
{
  "items": [
    {
      "data": "2026-04-02T14:32:00Z",
      "nomeUsuario": "Secretária Maria",
      "acao": "Cadastro de Aluno",
      "entidade": "João Silva",
      "status": "Sucesso"
    },
    {
      "data": "2026-04-02T13:15:00Z",
      "nomeUsuario": "Admin Master",
      "acao": "Criação de Usuário",
      "entidade": "Prof. Carlos",
      "status": "Sucesso"
    }
  ],
  "total": 2
}
```

---

### 3. **Endpoint: GET /api/admin/status-sistema**

**Descrição:** Retorna informações sobre o status do sistema.

**Método:** GET

**Autenticação:** Requerida (header Authorization)

**Resposta de Sucesso (200):**
```json
{
  "bancoDados": {
    "status": "OK",
    "descricao": "Online - Funcionando"
  },
  "armazenamento": {
    "percentualUso": 73,
    "descricao": "Limite de Alerta: 80%"
  },
  "ultimaSincronizacao": {
    "data": "2026-04-02T12:35:00Z",
    "descricao": "Há 2 horas"
  }
}
```

---

## 👥 Lista de Usuários - Administrador

### 4. **Endpoint: GET /api/admin/usuarios**

**Descrição:** Retorna a lista de usuários do sistema com filtros.

**Método:** GET

**Autenticação:** Requerida

**Query Parameters:**
- `busca` (opcional): Filtrar por nome, email ou matrícula
- `perfil` (opcional): Filtrar por perfil (administrador, secretaria, psicopedagogo, professor, diretor)
- `status` (opcional): Filtrar por status (ativo, inativo, bloqueado)
- `unidade_id` (opcional): Filtrar por unidade escolar
- `limite` (opcional): Resultados por página (padrão: 10)
- `pagina` (opcional): Número da página (padrão: 1)

**Resposta de Sucesso (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nome_completo": "Maria da Silva",
      "email": "maria@escola.edu.br",
      "perfil_nome": "Secretaria",
      "unidade_id": 1,
      "status": "ativo",
      "ultimo_login_em": "2026-04-02T13:20:00Z"
    }
  ],
  "total": 47,
  "pagina": 1,
  "limite": 10
}
```

---

## 🏫 Lista de Unidades - Administrador

### 5. **Endpoint: GET /api/admin/unidades**

**Descrição:** Retorna a lista de unidades escolares.

**Método:** GET

**Autenticação:** Requerida

**Query Parameters:**
- `busca` (opcional): Filtrar por nome, cidade ou CNPJ
- `estado` (opcional): Filtrar por UF
- `status` (opcional): Filtrar por status (ativa, inativa, manutencao)
- `limite` (opcional): Resultados por página
- `pagina` (opcional): Número da página

**Resposta de Sucesso (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "Escola Municipal Centro",
      "cidade": "São Paulo",
      "cnpj": "12.345.678/0001-90",
      "diretor_nome": "Prof. Roberto Silva",
      "estado": "SP",
      "status": "ativa"
    }
  ],
  "total": 12
}
```

---

## 📊 Relatórios - Administrador

### 6. **Endpoint: GET /api/admin/relatorios/dashboard**

**Descrição:** Retorna dados consolidados para o painel de relatórios.

**Método:** GET

**Autenticação:** Requerida

**Query Parameters:**
- `periodo` (opcional): Período de análise (30dias, trimestre, ano) - padrão: 30dias
- `unidade_id` (opcional): Filtrar por unidade
- `serie` (opcional): Filtrar por série
- `tipo_neurodiversidade` (opcional): Filtrar por tipo

**Resposta de Sucesso (200):**
```json
{
  "totalAlunos": 1247,
  "comLaudos": 342,
  "emAcompanhamento": 128,
  "encaminhamentosPendentes": 45,
  "distribuicaoNeurodiversidade": {
    "autismo": 120,
    "tdah": 95,
    "altasHabilidades": 68,
    "deficienciaAuditiva": 42,
    "outros": 17
  },
  "alunosPorSerie": {
    "educacaoInfantil": 320,
    "1ao3ano": 285,
    "4ao5ano": 340,
    "6ao9ano": 302
  },
  "resumoPorUnidade": [
    {
      "nomeUnidade": "Escola Municipal Centro",
      "totalAlunos": 325,
      "comLaudos": 92,
      "emAcompanhamento": 28,
      "taxaAbrangencia": 28.3
    }
  ]
}
```

---

## 🔐 Autenticação

### 7. **Endpoint: POST /api/auth/logout**

**Descrição:** Realiza logout do usuário.

**Método:** POST

**Autenticação:** Requerida

**Resposta de Sucesso (200):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

---

## 📝 Auditoria

### 8. **Endpoint: GET /api/admin/auditoria**

**Descrição:** Retorna registros de auditoria do sistema.

**Método:** GET

**Autenticação:** Requerida

**Query Parameters:**
- `usuario` (opcional): Filtrar por nome de usuário
- `tipo` (opcional): Filtrar por tipo de ação (Criação, Atualização, Exclusão, Login, Logout)
- `data_inicio` (opcional): Data inicial (formato: YYYY-MM-DD)
- `data_fim` (opcional): Data final (formato: YYYY-MM-DD)
- `limite`: Resultados por página
- `pagina`: Número da página

**Resposta de Sucesso (200):**
```json
{
  "items": [
    {
      "data": "2026-04-02T14:35:00Z",
      "nomeUsuario": "Admin Master",
      "acao": "Criação",
      "entidade": "Usuário",
      "detalhes": "Maria da Silva (maria@escola.edu.br)",
      "resultado": "Sucesso"
    }
  ],
  "total": 1247,
  "resumo": {
    "totalAcoes": 1247,
    "criacoes": 542,
    "atualizacoes": 634,
    "exclusoes": 71
  }
}
```

---

## 📊 Alunos - Nível Central

### 9. **Endpoint: GET /api/admin/alunos**

**Descrição:** Retorna lista de alunos com filtros avançados.

**Método:** GET

**Autenticação:** Requerida

**Query Parameters:**
- `busca` (opcional): Filtrar por nome, CPF ou matrícula
- `unidade_id` (opcional): Filtrar por unidade
- `serie` (opcional): Filtrar por série
- `diagnostico` (opcional): Filtrar por diagnóstico
- `status` (opcional): Filtrar por status
- `limite`: Resultados por página
- `pagina`: Número da página

**Resposta de Sucesso (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "João Silva",
      "matricula": "MAT20240001",
      "unidade": "Escola Municipal Centro",
      "serie": "1º ano",
      "diagnostico": "Autismo",
      "status": "ativo"
    }
  ],
  "total": 1247
}
```

---

## ⚠️ Tratamento de Erros

Todos os endpoints devem retornar erros no seguinte formato:

**Erro 401 - Não Autorizado:**
```json
{
  "message": "Acesso não autorizado",
  "code": "UNAUTHORIZED"
}
```

**Erro 403 - Proibido:**
```json
{
  "message": "Você não tem permissão para acessar este recurso",
  "code": "FORBIDDEN"
}
```

**Erro 404 - Não Encontrado:**
```json
{
  "message": "Recurso não encontrado",
  "code": "NOT_FOUND"
}
```

**Erro 500 - Erro Interno do Servidor:**
```json
{
  "message": "Erro interno do servidor",
  "code": "INTERNAL_SERVER_ERROR"
}
```

---

## 🔄 Padrões de Resposta

### Headers Requeridos

Todas as requisições devem incluir:
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Formato de Data/Hora

Todas as datas devem estar em formato ISO 8601 com timezone:
```
2026-04-02T14:35:00Z
```

### Paginação

Endpoints que retornam listas devem seguir este padrão:
```json
{
  "items": [...],
  "total": 100,
  "pagina": 1,
  "limite": 10,
  "totalPaginas": 10
}
```

---

## 🚀 Próximos Passos

1. Implementar endpoints básicos do dashboard
2. Adicionar autenticação JWT
3. Implementar sistemas de filtros e paginação
4. Adicionar tratamento de erros padronizado
5. Implementar cache para melhor performance
6. Adicionar logging e auditoria

---

**Versão:** 1.0
**Data:** 10/04/2026
**Status:** Em Preparação
