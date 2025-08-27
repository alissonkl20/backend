from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime
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

# Blueprint principal
main_bp = Blueprint('main', __name__)

# ========== FUNÇÕES AUXILIARES ==========
def check_database(app):
    """Verifica e corrige estrutura do banco"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            if 'usuarios' not in inspector.get_table_names():
                db.create_all()
                return True
            
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            
            # Adicionar colunas faltantes
            if 'facebook_login' not in columns:
                db.session.execute(text('ALTER TABLE usuarios ADD COLUMN facebook_login BOOLEAN DEFAULT FALSE'))
            if 'facebook_id' not in columns:
                db.session.execute(text('ALTER TABLE usuarios ADD COLUMN facebook_id VARCHAR(100)'))
            
            db.session.commit()
            db.create_all()
            return True
            
        except Exception as e:
            print(f"❌ Erro no banco: {e}")
            db.drop_all()
            db.create_all()
            return True

def get_cardapio_data():
    """Obtém dados do cardápio formatados"""
    try:
        produtos = ProdutoModel.query.filter_by(usuario_id=current_user.id).all()
        categorias = {}
        
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

        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': categorias,
            'total_produtos': len(produtos),
            'usuario': current_user.nome
        }

    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        return {'erro': 'Erro ao carregar cardápio'}

# ========== ROTAS DE AUTENTICAÇÃO ==========
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password_sha256 = request.form.get("password")
        user = UsuarioModel.query.filter_by(email=email).first()

        if user and user.facebook_login:
            flash("Use o botão 'Continuar com Facebook'.", "warning")
            return render_template("login.html")

        if user and user.senha and Bcrypt.check_password_hash(user.senha, password_sha256):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(request.args.get("next") or url_for("main.dashboard"))
        
        flash("Login falhou. Verifique seu email e senha.", "danger")

    return render_template("login.html")

@main_bp.route("/facebook-login", methods=["POST"])
def facebook_login():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        facebook_id = data.get('id')
        
        if not all([email, name, facebook_id]):
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        if UsuarioModel.query.filter_by(email=email, facebook_login=False).first():
            return jsonify({'success': False, 'message': 'Email já cadastrado com login normal'}), 400
        
        user = UsuarioModel.query.filter_by(facebook_id=facebook_id).first()
        
        if not user:
            user = UsuarioModel.query.filter_by(email=email).first()
            if user:
                user.facebook_login = True
                user.facebook_id = facebook_id
                user.senha = None
            else:
                user = UsuarioModel(
                    nome=name, email=email, senha=None,
                    facebook_login=True, facebook_id=facebook_id
                )
                db.session.add(user)
            
            db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
        
    except Exception as e:
        print(f"❌ Erro no login Facebook: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro no servidor'}), 500

@main_bp.route("/cadastro_usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha_sha256 = request.form.get("password")
        confirmar_sha256 = request.form.get("confirm_password")

        if senha_sha256 != confirmar_sha256:
            flash("As senhas não coincidem.", "danger")
            return render_template("cadastro.html")

        if UsuarioModel.query.filter_by(email=email).first():
            flash("Este email já está em uso.", "danger")
            return render_template("cadastro.html")

        hashed_password = Bcrypt.generate_password_hash(senha_sha256).decode("utf-8")
        novo_usuario = UsuarioModel(nome=nome, email=email, senha=hashed_password)
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

# ========== ROTAS PRINCIPAIS ==========
@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user)

@main_bp.route("/create_product")
@login_required
def create_product():
    categorias = CategoriaModel.query.filter_by(usuario_id=current_user.id).all()
    return render_template("create_product.html", categorias=categorias)

@main_bp.route("/cardapio")
@login_required
def cardapio_html():
    try:
        dados = get_cardapio_data()
        return render_template("cardapio.html", dados=dados, usuario=current_user)
    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        flash("Erro ao carregar cardápio", "error")
        return redirect(url_for("main.dashboard"))

# ========== ROTAS DE CATEGORIAS ==========
@main_bp.route('/categorias')
@login_required
def categorias_page():
    categorias = CategoriaRepository.listar_por_usuario(current_user.id)
    return render_template("categorias.html", categorias=categorias)

@main_bp.route('/create_categoria', methods=['GET', 'POST'])
@login_required
def create_categoria():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')

        if not nome:
            flash('Nome da categoria é obrigatório', 'error')
            return render_template("categoria_form.html")

        if CategoriaRepository.existe_por_nome_e_usuario(nome, current_user.id):
            flash('Já existe uma categoria com este nome', 'error')
            return render_template("categoria_form.html")

        categoria = CategoriaModel(nome=nome, descricao=descricao, usuario_id=current_user.id)
        CategoriaRepository.salvar(categoria)

        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('main.categorias_page'))

    return render_template("categoria_form.html")

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
            return render_template("categoria_form.html", categoria=categoria)

        if nome != categoria.nome and CategoriaRepository.existe_por_nome_e_usuario(nome, current_user.id):
            flash('Já existe uma categoria com este nome', 'error')
            return render_template("categoria_form.html", categoria=categoria)

        categoria.nome = nome
        categoria.descricao = descricao
        CategoriaRepository.salvar(categoria)

        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('main.categorias_page'))

    return render_template("categoria_form.html", categoria=categoria)

@main_bp.route('/delete_categoria/<int:id>', methods=['POST'])
@login_required
def delete_categoria(id):
    if CategoriaRepository.deletar_por_id_e_usuario(id, current_user.id):
        flash('Categoria excluída com sucesso!', 'success')
    else:
        flash('Categoria não encontrada', 'error')
    
    return redirect(url_for('main.categorias_page'))

# ========== FUNÇÃO CREATE_APP ==========
def create_app():
    if not os.environ.get("RENDER"):
        load_dotenv(Path(__file__).parent / ".env", override=True)

    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-padrao-mude-isso")

    database_url = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    bcrypt = Bcrypt(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        return UsuarioModel.query.get(int(user_id))

    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        check_database(app)
    
    return app

# ========== CONFIGURAÇÃO FINAL ==========
app = create_app()

if __name__ == "__main__":
    print("✅ Aplicativo pronto para produção")
    app.run(host="0.0.0.0", port=5000, debug=True)
