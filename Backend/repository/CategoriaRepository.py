from model.CategoriaModel import CategoriaModel
from extensions import db
from typing import List, Optional

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
    def buscar_por_id_e_usuario(id, usuario_id):
        return CategoriaModel.query.filter_by(id=id, usuario_id=usuario_id).first()
    
    @staticmethod
    def listar_todos():
        return CategoriaModel.query.all()
    
    @staticmethod
    def listar_por_usuario(usuario_id):
        return CategoriaModel.query.filter_by(usuario_id=usuario_id).all()
    
    @staticmethod
    def deletar_por_id(id):
        categoria = CategoriaModel.query.get(id)
        if categoria:
            db.session.delete(categoria)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def deletar_por_id_e_usuario(id, usuario_id):
        categoria = CategoriaModel.query.filter_by(id=id, usuario_id=usuario_id).first()
        if categoria:
            db.session.delete(categoria)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def existe_por_nome(nome):
        return CategoriaModel.query.filter_by(nome=nome).first() is not None

    @staticmethod
    def existe_por_nome_e_usuario(nome, usuario_id):
        return CategoriaModel.query.filter_by(nome=nome, usuario_id=usuario_id).first() is not None

    @staticmethod
    def atualizar(categoria):
        db.session.commit()
        return categoria
    
    @staticmethod
    def count_por_usuario(usuario_id):
        return CategoriaModel.query.filter_by(usuario_id=usuario_id).count()