from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime
import requests
from sqlalchemy import inspect, text

# Blueprints
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp

# Extensões
from extensions import db

# Modelos
from model.ProdutoModel import ProdutoModel
from model.CategoriaModel import CategoriaModel
from model.UserModel import UsuarioModel

# Repositórios
from repository.CategoriaRepository import CategoriaRepository

# Carrega variáveis do .env apenas em desenvolvimento
if os.environ.get("RENDER") is None:
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

# Cria a instância do Flask
app = Flask(__name__, template_folder="templates")

# Cria um blueprint principal
main_bp = Blueprint('main', __name__)

# Configuração de segurança
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-padrao-mude-isso")

# Configuração do Facebook
FACEBOOK_APP_ID = os.environ.get("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET", "")

# Configuração do banco
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa extensões
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "main.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return UsuarioModel.query.get(int(user_id))

# DEBUG: Verificar se a pasta templates existe
template_path = Path(__file__).parent / "templates"
print(f"📁 Caminho dos templates: {template_path}")

if template_path.exists():
    templates = list(template_path.glob("*.html"))
    print(f"📄 Templates encontrados: {[t.name for t in templates]}")
else:
    print("❌ Pasta templates não encontrada!")
    template_path.mkdir(exist_ok=True)
    print("✅ Pasta templates criada")

# Função para verificar e corrigir a estrutura do banco
def check_and_fix_database():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # Verificar se a tabela usuarios existe
            if 'usuarios' not in inspector.get_table_names():
                print("🗃️ Tabela 'usuarios' não existe. Criando todas as tabelas...")
                db.create_all()
                return True
            
            # Verificar colunas da tabela usuarios
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            print(f"📊 Colunas na tabela usuarios: {columns}")
            
            # Adicionar colunas faltantes se necessário
            columns_to_add = []
            if 'facebook_login' not in columns:
                columns_to_add.append('facebook_login BOOLEAN DEFAULT FALSE')
            if 'facebook_id' not in columns:
                columns_to_add.append('facebook_id VARCHAR(100)')
            
            if columns_to_add:
                print("🔄 Adicionando colunas faltantes...")
                for column in columns_to_add:
                    try:
                        db.session.execute(text(f'ALTER TABLE usuarios ADD COLUMN {column}'))
                        print(f"   ➕ Adicionada coluna: {column.split()[0]}")
                    except Exception as e:
                        print(f"   ❌ Erro ao adicionar coluna: {e}")
                
                db.session.commit()
            
            # Criar outras tabelas se necessário
            db.create_all()
            print("✅ Estrutura do banco verificada e corrigida!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
            print("🔄 Recriando todas as tabelas...")
            db.drop_all()
            db.create_all()
            print("✅ Todas as tabelas recriadas!")
            return True

# Verificar e corrigir o banco ao iniciar
check_and_fix_database()

# ========== ROTAS DE AUTENTICAÇÃO ==========

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password_sha256 = request.form.get("password")

        user = UsuarioModel.query.filter_by(email=email).first()

        # Verificar se é usuário do Facebook
        if user and user.facebook_login:
            flash("Este email está registrado com Facebook. Use o botão 'Continuar com Facebook'.", "warning")
            return render_template("login.html")

        # Comparar bcrypt(SHA-256) com hash do banco
        if user and user.senha and bcrypt.check_password_hash(user.senha, password_sha256):
            login_user(user)
            next_page = request.args.get("next")
            flash("Login realizado com sucesso!", "success")
            return redirect(next_page or url_for("main.dashboard"))
        
        flash("Login falhou. Verifique seu email e senha.", "danger")

    return render_template("login.html")

@main_bp.route("/facebook-login", methods=["POST"])
def facebook_login():
    try:
        data = request.get_json()
        access_token = data.get('accessToken')
        email = data.get('email')
        name = data.get('name')
        facebook_id = data.get('id')
        
        # Validação básica
        if not email or not name or not facebook_id:
            return jsonify({
                'success': False, 
                'message': 'Dados do Facebook incompletos'
            }), 400
        
        # Verificar se já existe usuário com este email (não Facebook)
        existing_normal_user = UsuarioModel.query.filter_by(email=email, facebook_login=False).first()
        if existing_normal_user:
            return jsonify({
                'success': False, 
                'message': 'Este email já está cadastrado com login normal. Use seu email e senha.'
            }), 400
        
        # Verificar se o usuário já existe pelo Facebook ID
        user = UsuarioModel.query.filter_by(facebook_id=facebook_id).first()
        
        if not user:
            # Verificar se existe pelo email (usuário migrando para Facebook)
            user = UsuarioModel.query.filter_by(email=email).first()
            if user:
                # Atualizar usuário existente para login Facebook
                user.facebook_login = True
                user.facebook_id = facebook_id
                user.senha = None
            else:
                # Criar novo usuário para login com Facebook
                user = UsuarioModel(
                    nome=name, 
                    email=email, 
                    senha=None,
                    facebook_login=True,
                    facebook_id=facebook_id
                )
                db.session.add(user)
            
            db.session.commit()
        
        # Fazer login do usuário
        login_user(user)
        
        return jsonify({
            'success': True, 
            'message': 'Login realizado com sucesso',
            'redirect': url_for('main.dashboard')
        })
        
    except Exception as e:
        print(f"❌ Erro no login com Facebook: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Erro no servidor. Tente novamente.'
        }), 500

@main_bp.route("/cadastro_usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha_sha256 = request.form.get("password")
        confirmar_sha256 = request.form.get("confirm_password")

        # Verificar se é um usuário do Facebook
        existing_facebook_user = UsuarioModel.query.filter_by(email=email, facebook_login=True).first()
        if existing_facebook_user:
            flash("Este email já está registrado com Facebook. Use o botão 'Continuar com Facebook' para fazer login.", "warning")
            return render_template("cadastro.html")

        if senha_sha256 != confirmar_sha256:
            flash("As senhas não coincidem.", "danger")
            return render_template("cadastro.html")

        if UsuarioModel.query.filter_by(email=email).first():
            flash("Este email já está em uso.", "danger")
            return render_template("cadastro.html")

        # Salvar bcrypt(SHA-256)
        hashed_password = bcrypt.generate_password_hash(senha_sha256).decode("utf-8")
        novo_usuario = UsuarioModel(
            nome=nome, 
            email=email, 
            senha=hashed_password,
            facebook_login=False
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "success")
        return redirect(url_for("main.login"))

    return render_template("cadastro.html")

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("main.login"))

# Função para obter dados do cardápio
def get_cardapio_data():
    try:
        produtos = ProdutoModel.query.filter_by(usuario_id=current_user.id).all()
        categorias = {}
        total_produtos = 0

        for produto in produtos:
            if produto.categoria:
                nome_cat = produto.categoria.nome
                if nome_cat not in categorias:
                    categorias[nome_cat] = {'disponiveis': [], 'indisponiveis': []}

                item = {
                    'id': produto.id,
                    'nome': produto.nome, 
                    'preco': float(produto.preco),
                    'descricao': produto.descricao
                }
                
                if produto.disponivel:
                    categorias[nome_cat]['disponiveis'].append(item)
                else:
                    categorias[nome_cat]['indisponiveis'].append(item)

                total_produtos += 1

        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': categorias,
            'total_produtos': total_produtos,
            'usuario': current_user.nome
        }

    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': {},
            'total_produtos': 0,
            'erro': 'Erro ao carregar cardápio'
        }

# Rotas protegidas
@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user)

@main_bp.route("/create_product", methods=["GET", "POST"])
@login_required
def create_product():
    categorias = CategoriaModel.query.filter_by(usuario_id=current_user.id).all()
    return render_template("create_product.html", usuario=current_user, categorias=categorias)

@main_bp.route("/cadastro")
def cadastro_redirect():
    return redirect(url_for("main.create_product"))

@main_bp.route("/cardapio")
@login_required
def cardapio_html():
    dados = get_cardapio_data()
    return render_template("cardapio.html", dados=dados, usuario=current_user)

# ========== ROTAS PARA CATEGORIAS ==========

@main_bp.route('/categorias')
@login_required
def categorias_page():
    categorias = CategoriaRepository.listar_por_usuario(current_user.id)
    return render_template("categorias.html", categorias=categorias, usuario=current_user)

@main_bp.route('/create_categoria', methods=['GET', 'POST'])
@login_required
def create_categoria():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')
        
        if not nome:
            flash('Nome da categoria é obrigatório', 'error')
            return render_template("create_categoria.html")
        
        # Verificar se categoria já existe
        if CategoriaRepository.existe_por_nome_e_usuario(nome, current_user.id):
            flash('Já existe uma categoria com este nome', 'error')
            return render_template("create_categoria.html")
        
        # Criar nova categoria
        categoria = CategoriaModel(
            nome=nome,
            descricao=descricao,
            usuario_id=current_user.id
        )
        CategoriaRepository.salvar(categoria)
        
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('main.categorias_page'))
    
    return render_template("create_categoria.html")

@main_bp.route('/edit_categoria/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_categoria(id):
    categoria = CategoriaRepository.buscar_por_id_e_usuario(id, current_user.id)
    if not categoria:
        flash('Categoria não encontrada', 'error')
        return redirect(url_for('main.categorias_page'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')
        
        if not nome:
            flash('Nome da categoria é obrigatório', 'error')
            return render_template("edit_categoria.html", categoria=categoria)
        
        # Verificar se categoria já existe (excluindo a atual)
        if nome != categoria.nome and CategoriaRepository.existe_por_nome_e_usuario(nome, current_user.id):
            flash('Já existe uma categoria com este nome', 'error')
            return render_template("edit_categoria.html", categoria=categoria)
        
        categoria.nome = nome
        categoria.descricao = descricao
        CategoriaRepository.salvar(categoria)
        
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('main.categorias_page'))
    
    return render_template("edit_categoria.html", categoria=categoria)

@main_bp.route('/delete_categoria/<int:id>', methods=['POST'])
@login_required
def delete_categoria(id):
    if CategoriaRepository.deletar_por_id_e_usuario(id, current_user.id):
        flash('Categoria excluída com sucesso!', 'success')
    else:
        flash('Categoria não encontrada', 'error')
    
    return redirect(url_for('main.categorias_page'))

# Rotas de debug
@main_bp.route('/debug')
def debug():
    return render_template('debug.html')

@main_bp.route('/debug/database')
def debug_database():
    usuarios = UsuarioModel.query.all()
    categorias = CategoriaModel.query.all()
    produtos = ProdutoModel.query.all()
    
    return f"""
    <h1>Debug Database</h1>
    <p>Usuários: {len(usuarios)}</p>
    <p>Categorias: {len(categorias)}</p>
    <p>Produtos: {len(produtos)}</p>
    """

@main_bp.route('/debug/routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    
    return render_template('debug_routes.html', routes=routes)

@main_bp.route('/debug/templates')
def debug_templates():
    template_files = []
    template_path = Path(app.template_folder)
    
    if template_path.exists():
        for file in template_path.glob('*.html'):
            template_files.append(file.name)
    
    return f"""
    <h1>Debug Templates</h1>
    <p>Templates encontrados: {', '.join(template_files)}</p>
    """

# REGISTRA OS BLUEPRINTS APÓS DEFINIR TODAS AS ROTAS
app.register_blueprint(categoria_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    print("🌐 Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule} -> {rule.endpoint}")
    
    print("✅ Aplicativo Flask criado com sucesso!")
    print("🌐 Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host="0.0.0.0")