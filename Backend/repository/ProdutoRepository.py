from typing import List, Optional
from extensions import db
from flask_cors import CORS
from model.ProdutoModel import ProdutoModel

class ProdutoRepository:

    @staticmethod
    def find_by_categoria_id(categoria_id: int) -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(categoria_id=categoria_id).all()

    @staticmethod
    def find_by_disponivel_true() -> List[ProdutoModel]:
        return ProdutoModel.query.filter_by(disponivel=True).all()

    @staticmethod
    def find_by_nome(nome: str) -> ProdutoModel:
        return ProdutoModel.query.filter_by(nome=nome).first()

    @staticmethod
    def find_by_nome_ignore_case(nome: str) -> Optional[ProdutoModel]:
        return ProdutoModel.query.filter(
            db.func.lower(ProdutoModel.nome) == db.func.lower(nome)
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
    def delete_by_id(id: int) -> bool:
        produto = ProdutoModel.query.get(id)
        if produto:
            db.session.delete(produto)
            db.session.commit()
            return True
        return False

    @staticmethod
    def find_all() -> List[ProdutoModel]:
        return ProdutoModel.query.all()