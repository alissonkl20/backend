from model.CategoriaModel import CategoriaModel
from extensions import db

class CategoriaRepository:
    
    @staticmethod
    def salvar(categoria):
        db.session.add(categoria)
        db.session.commit()
        return categoria
    
    @staticmethod
    def buscar_por_id(id):
        return CategoriaModel.query.get(id)
    
    @staticmethod
    def listar_todos():
        return CategoriaModel.query.all()
    
    @staticmethod
    def deletar_por_id(id):
        categoria = CategoriaModel.query.get(id)
        if categoria:
            db.session.delete(categoria)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def existe_por_nome(nome):
        return CategoriaModel.query.filter_by(nome=nome).first() is not None

    @staticmethod
    def atualizar(categoria):
        db.session.commit()
        return categoria