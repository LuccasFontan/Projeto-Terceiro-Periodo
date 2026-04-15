# Exemplo de Implementação do Backend - Flask

Este é um exemplo de como implementar os endpoints da API SAADI usando Flask.

## Instalação de Dependências

```bash
pip install flask flask-cors python-dotenv flask-jwt-extended
```

## Estrutura de Diretórios Recomendada

```
backend/
├── __init__.py
├── config.py
├── extensions.py
├── routes/
│   ├── __init__.py
│   ├── admin_dashboard.py
│   ├── admin_usuarios.py
│   ├── admin_unidades.py
│   ├── admin_relatorios.py
│   ├── admin_auditoria.py
│   ├── auth.py
│   └── ...
├── models/
│   ├── __init__.py
│   ├── usuario.py
│   ├── unidade.py
│   ├── aluno.py
│   └── ...
└── decorators.py
```

## Exemplo de Rota: Dashboard do Administrador

**Arquivo: backend/routes/admin_dashboard.py**

```python
from flask import Blueprint, jsonify, request
from decorators import autenticado, requer_admin
from models import db, Usuario, Unidade, Aluno

dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/api/admin')

@dashboard_bp.route('/dashboard', methods=['GET'])
@autenticado
@requer_admin
def obter_dashboard():
    """Retorna as estatísticas principais do painel."""
    try:
        total_unidades = db.session.query(Unidade).count()
        usuarios_ativos = db.session.query(Usuario).filter_by(status='ativo').count()
        
        # Calcular configurações pendentes (exemplo)
        configuracoes_pendentes = 0  # Implementar lógica real
        
        # Calcular alertas de segurança (exemplo)
        alertas = 0  # Implementar lógica real
        
        return jsonify({
            'totalUnidades': total_unidades,
            'usuariosAtivos': usuarios_ativos,
            'configuracoesPendentes': configuracoes_pendentes,
            'alertaSeguranca': alertas
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erro ao carregar dados do dashboard'}), 500


@dashboard_bp.route('/atividades-recentes', methods=['GET'])
@autenticado
@requer_admin
def obter_atividades_recentes():
    """Retorna as últimas atividades do sistema."""
    limite = request.args.get('limite', 5, type=int)
    
    try:
        # Implementar consulta ao banco de dados
        atividades = [
            # {
            #     'data': '2026-04-02T14:32:00Z',
            #     'nomeUsuario': 'Secretária Maria',
            #     'acao': 'Cadastro de Aluno',
            #     'entidade': 'João Silva',
            #     'status': 'Sucesso'
            # }
        ]
        
        return jsonify({
            'items': atividades,
            'total': len(atividades)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erro ao carregar atividades'}), 500


@dashboard_bp.route('/status-sistema', methods=['GET'])
@autenticado
@requer_admin
def obter_status_sistema():
    """Retorna informações sobre o status do sistema."""
    try:
        return jsonify({
            'bancoDados': {
                'status': 'OK',
                'descricao': 'Online - Funcionando'
            },
            'armazenamento': {
                'percentualUso': 73,
                'descricao': 'Limite de Alerta: 80%'
            },
            'ultimaSincronizacao': {
                'data': '2026-04-02T12:35:00Z',
                'descricao': 'Há 2 horas'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erro ao carregar status do sistema'}), 500
```

## Exemplo de Rota: Lista de Usuários

**Arquivo: backend/routes/admin_usuarios.py**

```python
from flask import Blueprint, jsonify, request
from decorators import autenticado, requer_admin
from models import db, Usuario, Unidade
from sqlalchemy import or_

usuarios_bp = Blueprint('admin_usuarios', __name__, url_prefix='/api/admin')

@usuarios_bp.route('/usuarios', methods=['GET'])
@autenticado
@requer_admin
def listar_usuarios():
    """Retorna lista de usuários com filtros."""
    try:
        # Obter parâmetros de query
        busca = request.args.get('busca', '').lower()
        perfil = request.args.get('perfil', '').lower()
        status = request.args.get('status', '').lower()
        unidade_id = request.args.get('unidade_id', type=int)
        pagina = request.args.get('pagina', 1, type=int)
        limite = request.args.get('limite', 10, type=int)
        
        # Construir query base
        query = Usuario.query
        
        # Aplicar filtros
        if busca:
            query = query.filter(
                or_(
                    Usuario.nome_completo.ilike(f'%{busca}%'),
                    Usuario.email.ilike(f'%{busca}%'),
                    Usuario.matricula.ilike(f'%{busca}%')
                )
            )
        
        if perfil:
            query = query.filter(Usuario.perfil.ilike(perfil))
        
        if status:
            query = query.filter(Usuario.status.ilike(status))
        
        if unidade_id:
            query = query.filter(Usuario.unidade_id == unidade_id)
        
        # Paginar
        total = query.count()
        usuarios = query.limit(limite).offset((pagina - 1) * limite).all()
        
        # Preparar resposta
        items = [{
            'id': u.id,
            'nome_completo': u.nome_completo,
            'email': u.email,
            'perfil_nome': u.perfil,
            'unidade_id': u.unidade_id,
            'status': u.status,
            'ultimo_login_em': u.ultimo_login_em.isoformat() if u.ultimo_login_em else None
        } for u in usuarios]
        
        return jsonify({
            'items': items,
            'total': total,
            'pagina': pagina,
            'limite': limite,
            'totalPaginas': (total + limite - 1) // limite
        }), 200
        
    except Exception as e:
        print(f'Erro: {e}')
        return jsonify({'message': 'Erro ao carregar usuários'}), 500


@usuarios_bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@autenticado
@requer_admin
def deletar_usuario(usuario_id):
    """Deleta um usuário do sistema."""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Não permitir deletar admin master
        if usuario.perfil == 'administrador' and usuario.id == 1:
            return jsonify({'message': 'Não é possível deletar o admin master'}), 403
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao deletar usuário'}), 500
```

## Exemplo de Decorador: Autenticação

**Arquivo: backend/decorators.py**

```python
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import Usuario

def autenticado(f):
    """Verifica se o usuário está autenticado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Token inválido ou expirado'}), 401
    return decorated_function

def requer_admin(f):
    """Verifica se o usuário é administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            usuario = Usuario.query.get(user_id)
            
            if not usuario or usuario.perfil != 'administrador':
                return jsonify({'message': 'Acesso negado: apenas administradores'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Erro na verificação de permissões'}), 500
    
    return decorated_function

def requer_secretaria(f):
    """Verifica se o usuário é secretário ou admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            usuario = Usuario.query.get(user_id)
            
            if not usuario or usuario.perfil not in ['administrador', 'secretaria']:
                return jsonify({'message': 'Acesso negado'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Erro na verificação de permissões'}), 500
    
    return decorated_function
```

## Exemplo de Modelo: Usuário

**Arquivo: backend/models/usuario.py**

```python
from extensions import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='ativo')
    matricula = db.Column(db.String(50), unique=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'))
    ultimo_login_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    unidade = db.relationship('Unidade', backref='usuarios')
```

## Exemplo de Configuração: run.py

**Arquivo: run.py**

```python
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, jwt
from backend.routes.admin_dashboard import dashboard_bp
from backend.routes.admin_usuarios import usuarios_bp

def create_app():
    app = Flask(__name__)
    
    # Carregar configuração
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuarios_bp)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```

## Checklist de Implementação

- [ ] Configurar banco de dados (SQLAlchemy)
- [ ] Criar modelos de dados (Usuario, Unidade, Aluno, etc)
- [ ] Implementar autenticação JWT
- [ ] Criar rotas do dashboard
- [ ] Criar rotas de usuários
- [ ] Criar rotas de unidades
- [ ] Criar rotas de alunos
- [ ] Implementar filtros e paginação
- [ ] Adicionar validação de entrada
- [ ] Implementar tratamento de erros
- [ ] Adicionar logging
- [ ] Testes unitários
- [ ] Documentação da API
- [ ] Deploy em produção

---

**Próximo Passo:** Após preparar o painel principal, implementar os endpoints listados na especificação `BACKEND_API_SPEC.md`.
