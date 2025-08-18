from flask import Blueprint, request, jsonify, abort, render_template
from http import HTTPStatus
from decimal import Decimal
from model.ProdutoModel import ProdutoModel
from extensions import db
from model.CategoriaModel import CategoriaModel
from repository.ProdutoRepository import ProdutoRepository
from datetime import datetime

produto_bp = Blueprint('produtos', __name__, url_prefix='/api/produtos')
repo = ProdutoRepository()

@produto_bp.route('/', methods=['GET'])
def listar_produtos():
    produtos = repo.find_all()
    return jsonify([produto.to_dict() for produto in produtos])

@produto_bp.route('/', methods=['POST'])
def criar_produto():
    data = request.get_json()
    
    categoria_id = data.get('categoria_id') or (data.get('categoria', {}).get('id'))
    
    if not all([data.get('nome'), data.get('preco'), categoria_id]):
        abort(HTTPStatus.BAD_REQUEST, description="Campos obrigatórios faltando")
    
    try:
        categoria = CategoriaModel.query.get(categoria_id)
        if not categoria:
            abort(HTTPStatus.NOT_FOUND, description="Categoria não encontrada")
        
        produto = ProdutoModel(
            nome=data['nome'],
            preco=Decimal(str(data['preco'])),
            disponivel=data.get('disponivel', True),
            categoria=categoria
        )
        
        db.session.add(produto)
        db.session.commit()
        
        return jsonify(produto.to_dict()), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(e))

@produto_bp.route('/<int:id>', methods=['GET'])
def buscar_produto(id):
    produto = repo.find_by_id(id)
    if not produto:
        abort(HTTPStatus.NOT_FOUND)
    return jsonify(produto.to_dict())

@produto_bp.route('/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    produto = repo.find_by_id(id)
    if not produto:
        abort(HTTPStatus.NOT_FOUND)
    
    data = request.get_json()
    try:
        if 'nome' in data:
            produto.nome = data['nome']
        if 'preco' in data:
            produto.preco = Decimal(str(data['preco']))
        if 'disponivel' in data:
            produto.disponivel = data['disponivel']
        
        categoria_id = data.get('categoria_id') or (data.get('categoria', {}).get('id'))
        if categoria_id:
            categoria = CategoriaModel.query.get(categoria_id)
            if not categoria:
                abort(HTTPStatus.NOT_FOUND, description="Categoria não encontrada")
            produto.categoria = categoria
        
        db.session.commit()
        return jsonify(produto.to_dict())
        
    except Exception as e:
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(e))

@produto_bp.route('/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    produto = repo.find_by_id(id)
    if not produto:
        abort(HTTPStatus.NOT_FOUND)
    
    try:
        db.session.delete(produto)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(e))

@produto_bp.route('/nome/<string:nome>', methods=['PUT'])
def atualizar_produto_por_nome(nome):
    produto = ProdutoModel.query.filter_by(nome=nome).first()
    if not produto:
        abort(HTTPStatus.NOT_FOUND)
    
    data = request.get_json()
    try:
        if 'nome' in data:
            produto.nome = data['nome']
        if 'preco' in data:
            produto.preco = Decimal(str(data['preco']))
        if 'disponivel' in data:
            produto.disponivel = data['disponivel']
        
        categoria_id = data.get('categoria_id') or (data.get('categoria', {}).get('id'))
        if categoria_id:
            categoria = CategoriaModel.query.get(categoria_id)
            if not categoria:
                abort(HTTPStatus.NOT_FOUND, description="Categoria não encontrada")
            produto.categoria = categoria
        
        db.session.commit()
        return jsonify(produto.to_dict())
        
    except Exception as e:
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(e))

@produto_bp.route('/<string:nome>', methods=['DELETE'])
def deletar_produto_por_nome(nome):
    produto = ProdutoModel.query.filter_by(nome=nome).first()
    if not produto:
        abort(HTTPStatus.NOT_FOUND)
    
    try:
        db.session.delete(produto)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(e))


def get_cardapio_data() -> dict[str, any]:
    try:
        produtos: list[ProdutoModel] = repo.find_all()
        categorias = {}
        total_produtos = 0

        for produto in produtos:
            nome_cat = produto.categoria.nome  # pega exatamente do banco
            if nome_cat not in categorias:
                categorias[nome_cat] = {'disponiveis': [], 'indisponiveis': []}

            item = {'nome': produto.nome, 'preco': produto.preco}
            if produto.disponivel:
                categorias[nome_cat]['disponiveis'].append(item)
            else:
                categorias[nome_cat]['indisponiveis'].append(item)

            total_produtos += 1

        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': categorias,
            'total_produtos': total_produtos,
            'erro': None
        }

    except Exception as e:
        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': {},
            'total_produtos': 0,
            'erro': f'Erro ao carregar cardápio: {str(e)}'
        }
