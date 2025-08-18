from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from extensions import db

class ProdutoModel(db.Model):
    __tablename__ = 'produto'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(Numeric(10, 2), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    descricao = db.Column(db.String(500), nullable=True)
    
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    categoria = db.relationship("CategoriaModel", back_populates="produtos")
    
    def __init__(self, nome, preco, disponivel=True, categoria=None):
        self.nome = nome
        self.preco = preco
        self.disponivel = disponivel
        self.categoria = categoria
        
    def __repr__(self):
        return f'<Produto {self.nome} (R${self.preco})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': float(self.preco) if isinstance(self.preco, Decimal) else self.preco,
            'disponivel': self.disponivel,
            'categoria_id': self.categoria_id,
            'categoria_nome': self.categoria.nome if self.categoria else None
        }
