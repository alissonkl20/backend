from typing import List, Optional
from extensions import db
from model.ProdutoModel import ProdutoModel

class ProdutoRepository:

    @staticmethod
    def find_by_categoria_id(categoria_id: int) -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(categoria_id=categoria_id).all()
    
    @staticmethod
    def find_by_categoria_id_e_usuario(categoria_id: int, usuario_id: int) -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(categoria_id=categoria_id, usuario_id=usuario_id).all()

    @staticmethod
    def find_by_disponivel_true() -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(disponivel=True).all()
    
    @staticmethod
    def find_by_disponivel_true_e_usuario(usuario_id: int) -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(disponivel=True, usuario_id=usuario_id).all()

    @staticmethod
    def find_by_nome(nome: str) -> Optional[ProdutoModel]:
        return ProdutoModel.query.filter_by(nome=nome).first()
    
    @staticmethod
    def find_by_nome_e_usuario(nome: str, usuario_id: int) -> Optional[ProdutoModel]:
        return ProdutoModel.query.filter_by(nome=nome, usuario_id=usuario_id).first()

    @staticmethod
    def find_by_nome_ignore_case(nome: str) -> Optional[ProdutoModel]:
        return ProdutoModel.query.filter(
            db.func.lower(ProdutoModel.nome) == db.func.lower(nome)
        ).first()
    
    @staticmethod
    def find_by_nome_ignore_case_e_usuario(nome: str, usuario_id: int) -> Optional[ProdutoModel]:
        return ProdutoModel.query.filter(
            db.func.lower(ProdutoModel.nome) == db.func.lower(nome),
            ProdutoModel.usuario_id == usuario_id
        ).first()

    # Basic CRUD operations
    @staticmethod
    def save(produto: ProdutoModel) -> ProdutoModel:
        db.session.add(produto)
        db.session.commit()
        return produto

    @staticmethod
    def find_by_id(id: int) -> Optional[ProdutoModel]:
        return ProdutoModel.query.get(id)
    
    @staticmethod
    def find_by_id_e_usuario(id: int, usuario_id: int) -> Optional[ProdutoModel]:
        return ProdutoModel.query.filter_by(id=id, usuario_id=usuario_id).first()

    @staticmethod
    def delete_by_id(id: int) -> bool:
        produto = ProdutoModel.query.get(id)
        if produto:
            db.session.delete(produto)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def delete_by_id_e_usuario(id: int, usuario_id: int) -> bool:
        produto = ProdutoModel.query.filter_by(id=id, usuario_id=usuario_id).first()
        if produto:
            db.session.delete(produto)
            db.session.commit()
            return True
        return False

    @staticmethod
    def find_all() -> List[ProdutoModel]:
        return ProdutoModel.query.all()
    
    @staticmethod
    def find_by_usuario(usuario_id: int) -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(usuario_id=usuario_id).all()
    
    @staticmethod
    def count_by_usuario(usuario_id: int) -> int:
        return ProdutoModel.query.filter_by(usuario_id=usuario_id).count()
    
    @staticmethod
    def count_disponiveis_by_usuario(usuario_id: int) -> int:
        return ProdutoModel.query.filter_by(usuario_id=usuario_id, disponivel=True).count()
    
    @staticmethod
    def count_por_categoria_e_usuario(categoria_id: int, usuario_id: int) -> int:
        return ProdutoModel.query.filter_by(categoria_id=categoria_id, usuario_id=usuario_id).count()