from flask import Blueprint, request, jsonify, abort
from http import HTTPStatus
from decimal import Decimal
from model.ProdutoModel import ProdutoModel
from extensions import db
from model.CategoriaModel import CategoriaModel
from repository.ProdutoRepository import ProdutoRepository

produto_bp = Blueprint('produtos', __name__, url_prefix='/api/produtos')
repo = ProdutoRepository()

# Novo endpoint GET para listar todos os produtos
@produto_bp.route('/', methods=['GET'])
def listar_produtos():
    produtos = repo.find_all()
    return jsonify([produto.to_dict() for produto in produtos])

@produto_bp.route('/', methods=['POST'])
def criar_produto():
    data = request.get_json()
    
    required_fields = ['nome', 'preco', 'categoria_id']
    if not all(field in data for field in required_fields):
        abort(HTTPStatus.BAD_REQUEST, description="Campos obrigatórios faltando")
    
    try:
        # Busca a categoria primeiro
        categoria = CategoriaModel.query.get(data['categoria_id'])
        if not categoria:
            abort(HTTPStatus.NOT_FOUND, description="Categoria não encontrada")
        
        # Cria o produto passando o objeto categoria
        produto = ProdutoModel(
            nome=data['nome'],
            preco=Decimal(str(data['preco'])),
            disponivel=data.get('disponivel', True),
            categoria=categoria  # Agora passando o objeto, não o ID
        )
        
        db.session.add(produto)
        db.session.commit()
        
        return produto.to_dict(), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(e))

# ... (outros endpoints permanecem iguais) ...