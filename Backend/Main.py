from flask import Flask, render_template
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from pathlib import Path

# Importe os blueprints
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp, get_cardapio_data
from extensions import db

# Carrega variáveis do .env apenas em desenvolvimento
if os.environ.get('RENDER') is None:  # Só carrega .env se não estiver no Render
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Configuração do banco para Render - CORRIGIDO
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Corrige a URL para SQLAlchemy (Render usa postgres://, SQLAlchemy precisa postgresql://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback para desenvolvimento
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensões
    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    # Registra blueprints
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)

    # Rotas
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/cardapio')
    def cardapio_html():
        dashboard = get_cardapio_data()
        return render_template('cardapio.html', dados=dashboard)

    @app.route('/cadastro')
    def cadastro():
        return render_template('cadastro.html')

    return app

# Gunicorn espera a variável "app" no módulo
app = create_app()