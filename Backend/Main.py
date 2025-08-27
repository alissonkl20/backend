from flask import Flask
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import inspect, text
import os

# Importações de blueprints
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp

# Extensões
from extensions import db, bcrypt, login_manager, oauth

# Modelos
from model.UserModel import UsuarioModel

# Blueprint principal
from main_routes import main_bp

# ========== FUNÇÃO CREATE_APP ==========
def create_app():
    # Carregar variáveis de ambiente
    if not os.environ.get("RENDER"):
        load_dotenv(Path(__file__).parent / ".env", override=True)

    # Configuração do aplicativo Flask
    app = Flask(__name__, template_folder="templates")
    
    # Configurações
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-padrao-mude-isso")
    database_url = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Inicializar extensões
    initialize_extensions(app)
    
    # Registrar Blueprints
    register_blueprints(app)
    
    # Configurar banco de dados
    with app.app_context():
        check_database(app)
    
    return app

def initialize_extensions(app):
    """Inicializar todas as extensões Flask"""
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    
    # Configuração OAuth Google
    app.google = oauth.register(
        name='google',
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # Configurar login manager
    login_manager.login_view = "main.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(UsuarioModel, int(user_id))

def register_blueprints(app):
    """Registrar todos os blueprints"""
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(main_bp)

def check_database(app):
    """Verificar e configurar o banco de dados"""
    try:
        inspector = inspect(db.engine)
        if 'usuarios' not in inspector.get_table_names():
            db.create_all()
        
        # Verificar e adicionar colunas se necessário
        columns = [col['name'] for col in inspector.get_columns('usuarios')]
        if 'google_login' not in columns:
            db.session.execute(text('ALTER TABLE usuarios ADD COLUMN google_login BOOLEAN DEFAULT FALSE'))
        if 'google_id' not in columns:
            db.session.execute(text('ALTER TABLE usuarios ADD COLUMN google_id VARCHAR(100)'))
        
        # Remover NOT NULL da coluna senha se existir
        try:
            db.session.execute(text('ALTER TABLE usuarios ALTER COLUMN senha DROP NOT NULL'))
        except:
            pass  # Se já não tiver NOT NULL, ignora o erro
        
        db.session.commit()
        db.create_all()
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        db.drop_all()
        db.create_all()

app = create_app()

if __name__ == "__main__":
    print("✅ Aplicativo pronto para produção")
    app.run(host="0.0.0.0", port=5000, debug=False)  # debug=False em produção