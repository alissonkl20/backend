from flask import Blueprint, request, jsonify, abort
from http import HTTPStatus
from decimal import Decimal
from flask_login import login_required, current_user
from model.ProdutoModel import ProdutoModel
from extensions import db
from model.CategoriaModel import CategoriaModel
from repository.ProdutoRepository import ProdutoRepository
from datetime import datetime

produto_bp = Blueprint('produtos', __name__, url_prefix='/api/produtos')
repo = ProdutoRepository()

@produto_bp.route('/', methods=['GET'])
@login_required
def listar_produtos():
    try:
        produtos = repo.find_by_usuario(current_user.id)
        return jsonify([produto.to_dict() for produto in produtos])
    except Exception as e:
        print(f"❌ Erro ao listar produtos: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Erro interno do servidor")

@produto_bp.route('/', methods=['POST'])
@login_required
def criar_produto():
    try:
        data = request.get_json()
        print(f"📦 Dados recebidos no POST: {data}")
        
        if not data:
            abort(HTTPStatus.BAD_REQUEST, description="Nenhum dado fornecido")
        
        categoria_id = data.get('categoria_id') or (data.get('categoria', {}).get('id'))
        
        if not data.get('nome'):
            abort(HTTPStatus.BAD_REQUEST, description="Campo 'nome' é obrigatório")
        if not data.get('preco'):
            abort(HTTPStatus.BAD_REQUEST, description="Campo 'preco' é obrigatório")
        if not categoria_id:
            abort(HTTPStatus.BAD_REQUEST, description="Campo 'categoria_id' é obrigatório")
        
        categoria = CategoriaModel.query.filter_by(
            id=categoria_id, 
            usuario_id=current_user.id
        ).first()
        
        if not categoria:
            abort(HTTPStatus.NOT_FOUND, description=f"Categoria com ID {categoria_id} não encontrada")
        
        try:
            preco_decimal = Decimal(str(data['preco']))
        except (ValueError, TypeError):
            abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
        
        produto = ProdutoModel(
            nome=data['nome'],
            preco=preco_decimal,
            disponivel=data.get('disponivel', True),
            descricao=data.get('descricao', ''),
            categoria=categoria,
            usuario_id=current_user.id
        )
        
        db.session.add(produto)
        db.session.commit()
        
        print(f"✅ Produto criado com sucesso: {produto.nome} - R${produto.preco}")
        
        return jsonify(produto.to_dict()), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        print(f"🔥 ERRO DETALHADO ao criar produto: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/<int:id>', methods=['GET'])
@login_required
def buscar_produto(id):
    try:
        produto = repo.find_by_id_e_usuario(id, current_user.id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        return jsonify(produto.to_dict())
    except Exception as e:
        print(f"❌ Erro ao buscar produto {id}: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Erro interno do servidor")

@produto_bp.route('/<int:id>', methods=['PUT'])
@login_required
def atualizar_produto(id):
    try:
        produto = repo.find_by_id_e_usuario(id, current_user.id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        
        data = request.get_json()
        print(f"📦 Dados recebidos no PUT: {data}")
        
        if 'nome' in data:
            produto.nome = data['nome']
        if 'preco' in data:
            try:
                produto.preco = Decimal(str(data['preco']))
            except (ValueError, TypeError):
                abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
        if 'disponivel' in data:
            produto.disponivel = data['disponivel']
        if 'descricao' in data:
            produto.descricao = data['descricao']
        
        categoria_id = data.get('categoria_id') or (data.get('categoria', {}).get('id'))
        if categoria_id:
            categoria = CategoriaModel.query.filter_by(
                id=categoria_id, 
                usuario_id=current_user.id
            ).first()
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
@login_required
def deletar_produto(id):
    try:
        produto = repo.find_by_id_e_usuario(id, current_user.id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND)
        
        db.session.delete(produto)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar produto {id}: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/cardapio', methods=['GET'])
@login_required
def get_cardapio():
    try:
        produtos = repo.find_by_usuario(current_user.id)
        categorias = {}
        total_produtos = 0

        for produto in produtos:
            if produto.categoria:
                nome_cat = produto.categoria.nome
                if nome_cat not in categorias:
                    categorias[nome_cat] = {'disponiveis': [], 'indisponiveis': []}

                item = {
                    'id': produto.id,
                    'nome': produto.nome, 
                    'preco': float(produto.preco),
                    'descricao': produto.descricao
                }
                
                if produto.disponivel:
                    categorias[nome_cat]['disponiveis'].append(item)
                else:
                    categorias[nome_cat]['indisponiveis'].append(item)

                total_produtos += 1

        return jsonify({
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': categorias,
            'total_produtos': total_produtos,
            'usuario': current_user.nome
        })

    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro ao carregar cardápio: {str(e)}")