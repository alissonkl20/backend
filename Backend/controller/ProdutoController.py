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
    try:
        produtos = repo.find_all()
        return jsonify([produto.to_dict() for produto in produtos])
    except Exception as e:
        print(f"❌ Erro ao listar produtos: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Erro interno do servidor")

@produto_bp.route('/', methods=['POST'])
def criar_produto():
    try:
        data = request.get_json()
        print(f"📦 Dados recebidos no POST: {data}")  # DEBUG IMPORTANTE
        
        if not data:
            abort(HTTPStatus.BAD_REQUEST, description="Nenhum dado fornecido")
        
        # EXTRAI CATEGORIA_ID DE DUAS FORMAS POSSÍVEIS
        categoria_id = data.get('categoria_id') or (data.get('categoria', {}).get('id'))
        
        # VALIDAÇÃO DETALHADA DOS CAMPOS OBRIGATÓRIOS
        if not data.get('nome'):
            abort(HTTPStatus.BAD_REQUEST, description="Campo 'nome' é obrigatório")
        if not data.get('preco'):
            abort(HTTPStatus.BAD_REQUEST, description="Campo 'preco' é obrigatório")
        if not categoria_id:
            abort(HTTPStatus.BAD_REQUEST, description="Campo 'categoria_id' é obrigatório")
        
        # VERIFICA SE A CATEGORIA EXISTE
        categoria = CategoriaModel.query.get(categoria_id)
        if not categoria:
            abort(HTTPStatus.NOT_FOUND, description=f"Categoria com ID {categoria_id} não encontrada")
        
        # CONVERTE PREÇO PARA DECIMAL (com tratamento de erro)
        try:
            preco_decimal = Decimal(str(data['preco']))
        except (ValueError, TypeError):
            abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
        
        # CRIA O PRODUTO - CORRETO!
        produto = ProdutoModel(
            nome=data['nome'],
            preco=preco_decimal,
            disponivel=data.get('disponivel', True),
            categoria=categoria  # ✅ CORRETO - passa o objeto categoria
        )
        
        # ADICIONA E COMMITA
        db.session.add(produto)
        db.session.commit()
        
        print(f"✅ Produto criado com sucesso: {produto.nome} - R${produto.preco}")
        
        return jsonify(produto.to_dict()), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        print(f"🔥 ERRO DETALHADO ao criar produto: {str(e)}")
        print(f"📋 Tipo do erro: {type(e).__name__}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/<int:id>', methods=['GET'])
def buscar_produto(id):
    try:
        produto = repo.find_by_id(id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        return jsonify(produto.to_dict())
    except Exception as e:
        print(f"❌ Erro ao buscar produto {id}: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Erro interno do servidor")

@produto_bp.route('/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    try:
        produto = repo.find_by_id(id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        
        data = request.get_json()
        print(f"📦 Dados recebidos no PUT: {data}")  # DEBUG
        
        if 'nome' in data:
            produto.nome = data['nome']
        if 'preco' in data:
            try:
                produto.preco = Decimal(str(data['preco']))
            except (ValueError, TypeError):
                abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
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
        print(f"❌ Erro ao atualizar produto {id}: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    try:
        produto = repo.find_by_id(id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        
        db.session.delete(produto)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar produto {id}: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/nome/<string:nome>', methods=['PUT'])
def atualizar_produto_por_nome(nome):
    try:
        produto = ProdutoModel.query.filter_by(nome=nome).first()
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        
        data = request.get_json()
        print(f"📦 Dados recebidos no PUT por nome: {data}")  # DEBUG
        
        if 'nome' in data:
            produto.nome = data['nome']
        if 'preco' in data:
            try:
                produto.preco = Decimal(str(data['preco']))
            except (ValueError, TypeError):
                abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
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
        print(f"❌ Erro ao atualizar produto por nome '{nome}': {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/<string:nome>', methods=['DELETE'])
def deletar_produto_por_nome(nome):
    try:
        produto = ProdutoModel.query.filter_by(nome=nome).first()
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        
        db.session.delete(produto)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar produto por nome '{nome}': {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

def get_cardapio_data() -> dict[str, any]:
    try:
        produtos: list[ProdutoModel] = repo.find_all()
        categorias = {}
        total_produtos = 0

        for produto in produtos:
            if produto.categoria:  # ✅ VERIFICA SE CATEGORIA EXISTE
                nome_cat = produto.categoria.nome
                if nome_cat not in categorias:
                    categorias[nome_cat] = {'disponiveis': [], 'indisponiveis': []}

                item = {'nome': produto.nome, 'preco': float(produto.preco) if hasattr(produto.preco, 'quantize') else produto.preco}
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
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': {},
            'total_produtos': 0,
            'erro': f'Erro ao carregar cardápio: {str(e)}'
        }