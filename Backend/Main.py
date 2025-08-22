from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from pathlib import Path

# Blueprints
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp, get_cardapio_data

# Extensões
from extensions import db

# Modelos
from model.ProdutoModel import ProdutoModel
from model.CategoriaModel import CategoriaModel
from model.UserModel import UsuarioModel

# Carrega variáveis do .env apenas em desenvolvimento
if os.environ.get("RENDER") is None:
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

def create_app():
    app = Flask(__name__, template_folder="templates")

    # Configuração de segurança
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-padrao-mude-isso")

    # Configuração do banco
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializa extensões
    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        return UsuarioModel.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        print("✅ Tabelas criadas/verificadas!")

    # Blueprints
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)

    # Rotas de autenticação
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email")
            password_sha256 = request.form.get("password")  # já vem SHA-256 do frontend

            user = UsuarioModel.query.filter_by(email=email).first()

            # Comparar bcrypt(SHA-256) com hash do banco
            if user and bcrypt.check_password_hash(user.senha, password_sha256):
                login_user(user)
                next_page = request.args.get("next")
                flash("Login realizado com sucesso!", "success")
                return redirect(next_page or url_for("dashboard"))
            else:
                flash("Login falhou. Verifique seu email e senha.", "danger")

        return render_template("login.html")

    @app.route("/cadastro_usuario", methods=["GET", "POST"])
    def cadastro_usuario():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            nome = request.form.get("nome")
            email = request.form.get("email")
            senha_sha256 = request.form.get("password")  # já vem SHA-256
            confirmar_sha256 = request.form.get("confirm_password")

            if senha_sha256 != confirmar_sha256:
                flash("As senhas não coincidem.", "danger")
                return render_template("cadastro.html")

            if UsuarioModel.query.filter_by(email=email).first():
                flash("Este email já está em uso.", "danger")
                return render_template("cadastro.html")

            # Salvar bcrypt(SHA-256)
            hashed_password = bcrypt.generate_password_hash(senha_sha256).decode("utf-8")
            novo_usuario = UsuarioModel(nome=nome, email=email, senha=hashed_password)

            db.session.add(novo_usuario)
            db.session.commit()

            flash("Conta criada com sucesso! Faça login.", "success")
            return redirect(url_for("login"))

        return render_template("cadastro.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Você foi desconectado.", "info")
        return redirect(url_for("login"))

    # Rotas protegidas
    @app.route("/")
    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", usuario=current_user)

    @app.route("/create_product", methods=["GET", "POST"])
    @login_required
    def create_product():
        if request.method == "POST":
            # TODO: lógica de criação de produto
            pass
        return render_template("create_product.html", usuario=current_user)

    @app.route("/cadastro")
    def cadastro_redirect():
        return redirect(url_for("create_product"))

    @app.route("/cardapio")
    @login_required
    def cardapio_html():
        dados = get_cardapio_data()
        return render_template("cardapio.html", dados=dados, usuario=current_user)

    return app

# Instância para o Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
