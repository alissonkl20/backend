from flask import Flask
from flask_cors import CORS  # Corrigido: Import do pacote correto
from dotenv import load_dotenv
from pathlib import Path
from flask_migrate import Migrate  # Corrigido: Import do pacote correto
from extensions import db
import os
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp

# Configuração do .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def create_app():
    app = Flask(__name__)
    
    # Configurações ESSENCIAIS - CORRIGIDO: 'DATABASE_URI' (estava 'DATABASE_URI')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializações
    db.init_app(app)
    CORS(app)  # Agora usando o CORS correto
    migrate = Migrate(app, db)  # Inicialização correta do Flask-Migrate

    # Registrar Blueprints
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)

    # Rota de teste
    @app.route('/')
    def home():
        return "Backend conectado com sucesso! Rotas disponíveis: /api/categorias e /api/produtos"

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria todas as tabelas definidas nos models
    app.run()