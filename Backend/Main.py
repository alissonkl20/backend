from flask import Flask, render_template, redirect
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
from flask_migrate import Migrate
from Backend.extensions import db
import os
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp, get_cardapio_data
from datetime import datetime

# Configuração do .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)

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

# Variável global 'app' que o Gunicorn procura
app = create_app()

if __name__ == "__main__":
    # Executa localmente
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
