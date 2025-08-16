from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from extensions import db

class CategoriaModel(db.Model):
    __tablename__ = 'categoria'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False, unique=True)
    
    produtos = relationship("ProdutoModel", back_populates="categoria", cascade="all, delete-orphan")
    
    def __init__(self, nome):
        self.nome = nome
        
    def __repr__(self):
        return f'<Categoria {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
            # Excluding produtos to avoid circular references
        }