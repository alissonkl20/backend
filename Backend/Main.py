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

# Importe seus modelos PARA FORÇAR A CRIAÇÃO
from model.ProdutoModel import ProdutoModel
from model.CategoriaModel import CategoriaModel

# Carrega variáveis do .env apenas em desenvolvimento
if os.environ.get('RENDER') is None:
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Configurações do banco
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensões
    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    # CRIA TABELAS AUTOMATICAMENTE
    with app.app_context():
        db.create_all()
        print("✅ Tabelas criadas/com verificadas!")

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

app = create_app()