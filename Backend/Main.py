from flask import Flask, render_template, redirect, url_for, flash, Blueprint, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from pathlib import Path
from datetime import datetime
from sqlalchemy import inspect, text
import os

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

bcrypt = Bcrypt()

# ========== FUNÇÕES AUXILIARES ==========
def check_database(app):
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if 'usuarios' not in inspector.get_table_names():
                db.create_all()
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            if 'google_login' not in columns:
                db.session.execute(text('ALTER TABLE usuarios ADD COLUMN google_login BOOLEAN DEFAULT FALSE'))
            db.session.commit()
            db.create_all()
        except Exception as e:
            print(f"❌ Erro no banco: {e}")
            db.drop_all()
            db.create_all()

def get_cardapio_data():
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
@main_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@main_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("main.callback_google", _external=True)
    return current_app.google.authorize_redirect(redirect_uri)

@main_bp.route("/login/google/callback")
def callback_google():
    try:
        token = current_app.google.authorize_access_token()
        user_info = current_app.google.parse_id_token(token)
        email = user_info.get("email")
        name = user_info.get("name")

        if not email:
            flash("Não foi possível obter email do Google.", "danger")
            return redirect(url_for("main.login"))

        user = UsuarioModel.query.filter_by(email=email).first()
        if not user:
            user = UsuarioModel(
                nome=name,
                email=email,
                senha=None,
                google_login=True
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("main.dashboard"))

    except Exception as e:
        print("Erro login Google:", e)
        flash("Erro ao realizar login com Google.", "danger")
        return redirect(url_for("main.login"))

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

@main_bp.route('/categorias')
@login_required
def categorias_page():
    categorias = CategoriaRepository.listar_por_usuario(current_user.id)
    return render_template("categorias.html", categorias=categorias)

# ========== FUNÇÃO CREATE_APP ==========
def create_app():
    if not os.environ.get("RENDER"):
        load_dotenv(Path(__file__).parent / ".env", override=True)

    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-padrao-mude-isso")
    database_url = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        return UsuarioModel.query.get(int(user_id))

    # Configuração OAuth Google
    oauth = OAuth(app)
    app.google = oauth.register(
        name='google',
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url=os.environ.get("GOOGLE_DISCOVERY_URL"),
        client_kwargs={"scope": "openid email profile"}
    )

    # Registrar Blueprints
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        check_database(app)

    return app

app = create_app()

if __name__ == "__main__":
    print("✅ Aplicativo pronto para produção")
    app.run(host="0.0.0.0", port=5000, debug=True)
