from decimal import Decimal
from extensions import db
from sqlalchemy import Numeric
from sqlalchemy.orm import relationship

class ProdutoModel(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(Numeric(10, 2), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    descricao = db.Column(db.String(500), nullable=True)
    
    # Chaves estrangeiras
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamento com categoria - CORRIGIDO
    categoria = relationship("CategoriaModel", back_populates="produtos", foreign_keys=[categoria_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': float(self.preco),
            'disponivel': self.disponivel,
            'descricao': self.descricao,
            'categoria_id': self.categoria_id,
            'categoria_nome': self.categoria.nome if self.categoria else None,
            'usuario_id': self.usuario_id
        }
    
    def __repr__(self):
        return f'<Produto {self.nome} (R${self.preco})>'