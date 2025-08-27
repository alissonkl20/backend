from extensions import db
from flask_login import UserMixin

class UsuarioModel(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=True)  # Alterado para nullable=True
    google_login = db.Column(db.Boolean, default=False)
    google_id = db.Column(db.String(100), nullable=True)
    # ... outras colunas
    
    def __init__(self, nome, email, senha=None, google_login=False, google_id=None):
        self.nome = nome
        self.email = email
        self.senha = senha  # Pode ser None
        self.google_login = google_login
        self.google_id = google_id