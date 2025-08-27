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
        print(f"🔍 Listando produtos para usuário: {current_user.id}")
        
        produtos = repo.find_by_usuario(current_user.id)
        print(f"📊 Produtos encontrados: {len(produtos)}")
        
        produtos_data = []
        for produto in produtos:
            try:
                produto_dict = produto.to_dict()
                produtos_data.append(produto_dict)
            except Exception as e:
                print(f"⚠️ Erro ao serializar produto {produto.id}: {str(e)}")
                # Adiciona dados mínimos para evitar erro completo
                produtos_data.append({
                    'id': produto.id,
                    'nome': produto.nome,
                    'preco': float(produto.preco),
                    'erro': 'Erro na serialização'
                })
        
        return jsonify(produtos_data)
        
    except Exception as e:
        print(f"❌ ERRO ao listar produtos: {str(e)}")
        import traceback
        traceback.print_exc()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno do servidor: {str(e)}")

@produto_bp.route('/', methods=['POST'])
@login_required
def criar_produto():
    try:
        data = request.get_json()
        print(f"📦 Dados recebidos no POST: {data}")
        
        if not data:
            abort(HTTPStatus.BAD_REQUEST, description="Nenhum dado fornecido")
        
        categoria_id = data.get('categoria_id')
        
        # Validações obrigatórias
        required_fields = ['nome', 'preco', 'categoria_id']
        for field in required_fields:
            if not data.get(field):
                abort(HTTPStatus.BAD_REQUEST, description=f"Campo '{field}' é obrigatório")
        
        # Verifica se categoria existe e pertence ao usuário
        categoria = CategoriaModel.query.filter_by(
            id=categoria_id, 
            usuario_id=current_user.id
        ).first()
        
        if not categoria:
            abort(HTTPStatus.NOT_FOUND, description=f"Categoria com ID {categoria_id} não encontrada")
        
        # Converte preço para Decimal
        try:
            preco_decimal = Decimal(str(data['preco']))
        except (ValueError, TypeError):
            abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
        
        # Cria o produto
        produto = ProdutoModel(
            nome=data['nome'].strip(),
            preco=preco_decimal,
            quantidade=data.get('quantidade', 0),
            disponivel=data.get('disponivel', True),
            descricao=data.get('descricao', '').strip(),
            categoria_id=categoria_id,
            usuario_id=current_user.id
        )
        
        db.session.add(produto)
        db.session.commit()
        
        print(f"✅ Produto criado com sucesso: {produto.to_dict()}")
        
        return jsonify(produto.to_dict()), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERRO ao criar produto: {str(e)}")
        import traceback
        traceback.print_exc()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/<int:id>', methods=['GET'])
@login_required
def buscar_produto(id):
    try:
        produto = repo.find_by_id_e_usuario(id, current_user.id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND, description="Produto não encontrado")
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
            abort(HTTPStatus.NOT_FOUND, description="Produto não encontrado")
        
        data = request.get_json()
        print(f"📦 Dados recebidos no PUT: {data}")
        
        # Atualiza campos
        if 'nome' in data:
            produto.nome = data['nome'].strip()
        if 'preco' in data:
            try:
                produto.preco = Decimal(str(data['preco']))
            except (ValueError, TypeError):
                abort(HTTPStatus.BAD_REQUEST, description="Preço deve ser um número válido")
        if 'quantidade' in data:
            produto.quantidade = data['quantidade']
        if 'disponivel' in data:
            produto.disponivel = data['disponivel']
        if 'descricao' in data:
            produto.descricao = data['descricao'].strip()
        
        # Atualiza categoria se fornecida
        if 'categoria_id' in data:
            categoria_id = data['categoria_id']
            categoria = CategoriaModel.query.filter_by(
                id=categoria_id, 
                usuario_id=current_user.id
            ).first()
            if not categoria:
                abort(HTTPStatus.NOT_FOUND, description="Categoria não encontrada")
            produto.categoria_id = categoria_id
        
        db.session.commit()
        
        print(f"✅ Produto atualizado: {produto.to_dict()}")
        return jsonify(produto.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao atualizar produto {id}: {str(e)}")
        import traceback
        traceback.print_exc()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro interno: {str(e)}")

@produto_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def deletar_produto(id):
    try:
        produto = repo.find_by_id_e_usuario(id, current_user.id)
        if not produto:
            abort(HTTPStatus.NOT_FOUND, description="Produto não encontrado")
        
        db.session.delete(produto)
        db.session.commit()
        
        print(f"✅ Produto deletado: {id}")
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
                    'quantidade': produto.quantidade,
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
        import traceback
        traceback.print_exc()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Erro ao carregar cardápio: {str(e)}")

@produto_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'message': 'API de produtos está funcionando',
        'timestamp': datetime.now().isoformat()
    })