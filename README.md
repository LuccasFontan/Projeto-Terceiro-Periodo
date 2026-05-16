# SAADI - Sistema de Acompanhamento da Educação Inclusiva

<p align="center">
	<img src="frontend/assets/icons8-two-hands-48%20(1).png" alt="Logo SAADI" width="96">
</p>

O SAADI é uma plataforma web para organizar informações escolares de alunos com deficiência e apoiar o trabalho de equipes pedagógicas, psicopedagógicas e administrativas.

O projeto centraliza cadastros, acompanha encaminhamentos, registra relatórios e facilita a tomada de decisão na rotina escolar, contribuindo para um atendimento mais organizado e inclusivo.

## Sumário

- [Problema](#problema)
- [Proposta](#proposta)
- [Funcionalidades](#funcionalidades)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como executar](#como-executar)
- [Acessibilidade](#acessibilidade)
- [Agentes de IA](#agentes-de-ia)
- [Equipe](#equipe)
- [Licença](#licença)

## Problema

Muitas instituições ainda lidam com informações dispersas, processos manuais e pouca visibilidade sobre o histórico dos alunos que precisam de acompanhamento especializado. Isso dificulta a comunicação entre setores e reduz a eficiência no planejamento das ações pedagógicas.

## Proposta

O SAADI reduz essa fragmentação por meio de uma interface simples, padronizada e focada na gestão de dados escolares. A plataforma apoia o registro e a consulta de informações essenciais para o acompanhamento dos alunos ao longo do ano letivo.

## Funcionalidades

- Autenticação de acesso para perfis institucionais.
- Menus separados por área de atuação.
- Cadastro, atualização, listagem e exclusão de alunos, usuários e unidades.
- Controle de encaminhamentos e relatórios.
- Área específica para psicopedagogia e secretaria escolar.

## Estrutura do repositório

- `frontend/index.html`: página inicial de acesso.
- `frontend/css/`: estilos globais e específicos de cada módulo.
- `frontend/assets/`: imagens e ícones do sistema.
- `frontend/pages/auth/`: telas de autenticação.
- `frontend/pages/menus/administrador/`: área administrativa.
- `frontend/pages/menus/psicopedagogo/`: área do psicopedagogo.
- `frontend/pages/menus/secretaria/`: área da secretaria escolar.
- `frontend/js/`: scripts JavaScript da aplicação.
- `scripts/`: scripts de infraestrutura, como bootstrap do banco.

## Como executar

O frontend está em `frontend/` e continua sendo servido pelo Flask em `/`, então o uso normal segue funcionando pela aplicação backend.

## Backend Flask

O projeto agora inclui um backend em Flask com PostgreSQL, SQLAlchemy, Flask-Migrate, JWT e CORS.

### Dependências

Instale os pacotes do backend:

```bash
pip install -r requirements.txt
```

### Variáveis de ambiente

Copie `.env.example` para `.env` e configure:

- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`
- `SECRET_KEY`
- `JWT_SECRET_KEY`

### Inicialização do banco com migrações

```bash
flask --app run db init
flask --app run db migrate -m "initial"
flask --app run db upgrade
```

### Execução

```bash
python run.py
```

### Contrato de autenticação

- `POST /api/auth/login` valida as credenciais e o Backend injeta automaticamente um **Cookie HttpOnly** com o token JWT.
- O frontend envia `credentials: 'same-origin'` nos requests protegidos, garantindo o envio seguro do token sem expô-lo no `localStorage` (proteção contra XSS).

### Exemplo de fetch no frontend

```javascript
// Através do apiClient.js, a configuração de credentials é injetada
const response = await fetch('/api/admin/usuarios', {
	method: 'GET',
	credentials: 'same-origin', // OBRIGATÓRIO PARA ENVIAR O COOKIE
	headers: {
		'Accept': 'application/json'
	}
});

const data = await response.json();
```

## Banco de dados (PostgreSQL)

O projeto inclui um bootstrap de banco para facilitar o setup em qualquer PC.

1. Copie `.env.example` para `.env` e ajuste os dados de conexão.
2. Garanta que o PostgreSQL esteja ativo.
3. Rode o script:

```bash
python scripts/bootstrap_db.py
```

O script:

- Cria o banco configurado em `PGDATABASE` (se nao existir).
- Aplica o schema em `db/schema.sql`.
- Aplica dados iniciais em `db/seed.sql`.

## Acessibilidade

O projeto foi rigorosamente auditado e adaptado para conformidade com **WCAG 2.1 Nível AA**, incluindo:
- Navegação completa por teclado.
- Identificação clara de foco em elementos interativos.
- Suporte nativo a leitores de tela com labels ARIA e `aria-live`.
- Contraste de cores seguro e integração com VLibras em páginas específicas.

Para consultar a documentação de auditoria, leia [ACESSIBILIDADE.md](ACESSIBILIDADE.md).

## Agentes de IA

A manutenção do código deste repositório utiliza a força de times autônomos baseados em **Multi-Agent Frameworks** (padrão CrewAI), garantindo automações de desenvolvimento, auditorias de cibersegurança e Code Reviews automatizados.
Consulte o arquivo [agents.md](agents.md) para conhecer a nossa equipe de IA (Tech Lead, Desenvolvedor, Cyber Security e Code Reviewer).

## Equipe

- Jair Pereira Barcelos
- Lucas Fontan Fernandes

## Licença

Este projeto está sob a licença definida em [LICENSE](LICENSE).