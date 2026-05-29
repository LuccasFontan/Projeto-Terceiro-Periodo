# 🔐 Credenciais de Desenvolvimento (SAADI)

Este documento contém os usuários, senhas e perfis padrão pré-configurados para testes e desenvolvimento do sistema **SAADI** (Sistema de Apoio e Acompanhamento ao Desenvolvimento Inclusivo).

---

## 👥 Contas de Demonstração (Demo Accounts)

As contas abaixo são criadas automaticamente durante o processo de inicialização do banco de dados (`scripts/bootstrap_db.py`).

| Nome Completo | Perfil | E-mail | Matrícula | CPF | Senha Padrão |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Administrador SAADI** | 🏗️ Administrador | `admin@saadi.local` | `ADM001` | `111.111.111-11` | `Admin@12345!` |
| **Secretaria SAADI** | 💼 Secretaria | `secretaria@saadi.local` | `SEC001` | `222.222.222-22` | `Secretaria@12345!` |
| **Psicopedagogo SAADI** | 🔍 Psicopedagogo | `psicopedagogo@saadi.local` | `PSI001` | `333.333.333-33` | `Psicopedagogo@12345!` |

---

## 🛡️ Detalhes dos Perfis e Permissões

> [!NOTE]
> Cada perfil possui um escopo restrito de atuação dentro do sistema, garantindo a segurança dos dados sensíveis e a privacidade dos alunos (LGPD).

### 1. 🏗️ Administrador (`administrador`)
* **Escopo:** Acesso total e irrestrito a todas as configurações de sistema, auditoria e gerenciamento de entidades.
* **Principais Permissões:**
  * 👥 Criar, listar, atualizar e remover usuários.
  * 🏫 Criar, listar, atualizar e remover unidades de ensino.
  * ⚙️ Gerenciar parâmetros globais do sistema.
  * 📋 Visualizar logs de auditoria detalhados.
  * *Herda também todas as permissões dos demais perfis.*

### 2. 💼 Secretaria (`secretaria`)
* **Escopo:** Gestão de alunos e cadastros iniciais na respectiva unidade vinculada.
* **Principais Permissões:**
  * 🎒 Cadastrar, listar, atualizar e remover dados dos alunos.
  * 📨 Iniciar, listar e atualizar encaminhamentos escolares.
  * 📈 Listar relatórios gerais pedagógicos da unidade.

### 3. 🔍 Psicopedagogo (`psicopedagogo`)
* **Escopo:** Realização de triagens, criação de planos de intervenção e acompanhamento psicopedagógico.
* **Principais Permissões:**
  * 📋 Visualizar a listagem de alunos cadastrados.
  * 📑 Criar, listar e atualizar triagens e avaliações diagnósticas.
  * 🎯 Criar, editar e acompanhar planos de acompanhamento especializado (PDI).
  * 📝 Criar e exportar relatórios psicopedagógicos e laudos.

---

> [!WARNING]  
> **Aviso de Segurança**: Estas credenciais são destinadas exclusivamente para ambientes de **desenvolvimento e homologação**. Em ambientes de produção, as senhas devem ser alteradas imediatamente, e contas de teste não devem ser importadas.
