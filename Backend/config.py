import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Config:
    # Configurações do PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    
    # Configurações do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "True") == "True"
    
    # Configurações de CORS
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    CORS_SUPPORTS_CREDENTIALS = os.getenv("CORS_SUPPORTS_CREDENTIALS", "True") == "True"
    
    # Configurações do Flask
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "less")
    
    # Configuração adicional para SQLAlchemy Engine Options
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self):
        return {"echo": self.SQLALCHEMY_ECHO}

# Cria uma instância da configuração
config = Config()