from extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class UsuarioModel(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    
    # Relacionamentos - CORRIGIDOS
    categorias = relationship('CategoriaModel', backref='usuario', lazy=True, cascade='all, delete-orphan')
    produtos = relationship('ProdutoModel', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'quantidade_categorias': len(self.categorias),
            'quantidade_produtos': len(self.produtos)
        }