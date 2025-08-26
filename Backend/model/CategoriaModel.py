from extensions import db
from sqlalchemy.orm import relationship

class CategoriaModel(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    
    # Chave estrangeira para o usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamento com produtos - CORRIGIDO
    produtos = relationship('ProdutoModel', back_populates='categoria', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'usuario_id': self.usuario_id,
            'quantidade_produtos': len(self.produtos)
        }
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'