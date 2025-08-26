from flask import Blueprint, request, jsonify, abort
from http import HTTPStatus
from typing import List
from flask_login import login_required, current_user
from extensions import db
from model.CategoriaModel import CategoriaModel
from repository.CategoriaRepository import CategoriaRepository

categoria_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')

@categoria_bp.route('/', methods=['GET'])
@login_required
def listar_categorias():
    categorias: List[CategoriaModel] = CategoriaRepository.listar_por_usuario(current_user.id)
    return jsonify([categoria.to_dict() for categoria in categorias])

@categoria_bp.route('/', methods=['POST'])
@login_required
def criar_categoria():
    data = request.get_json()
    if not data or 'nome' not in data:
        abort(HTTPStatus.BAD_REQUEST, description="Nome da categoria é obrigatório")

    if CategoriaRepository.existe_por_nome_e_usuario(data['nome'], current_user.id):
        abort(HTTPStatus.CONFLICT, description="Categoria já existe")
    
    categoria = CategoriaModel(
        nome=data['nome'],
        descricao=data.get('descricao', ''),
        usuario_id=current_user.id
    )
    CategoriaRepository.salvar(categoria)
    return jsonify(categoria.to_dict()), HTTPStatus.CREATED

@categoria_bp.route('/<int:id>', methods=['GET'])
@login_required
def buscar_categoria(id: int):
    categoria = CategoriaRepository.buscar_por_id_e_usuario(id, current_user.id)
    if not categoria:
        abort(HTTPStatus.NOT_FOUND)
    return jsonify(categoria.to_dict())

@categoria_bp.route('/<int:id>', methods=['PUT'])
@login_required
def atualizar_categoria(id: int):
    categoria = CategoriaRepository.buscar_por_id_e_usuario(id, current_user.id)
    if not categoria:
        abort(HTTPStatus.NOT_FOUND)
    
    data = request.get_json()
    if not data or 'nome' not in data:
        abort(HTTPStatus.BAD_REQUEST, description="Nome da categoria é obrigatório")
    
    if data['nome'] != categoria.nome and CategoriaRepository.existe_por_nome_e_usuario(data['nome'], current_user.id):
        abort(HTTPStatus.CONFLICT, description="Categoria já existe")
    
    categoria.nome = data['nome']
    categoria.descricao = data.get('descricao', categoria.descricao)
    CategoriaRepository.salvar(categoria)
    
    return jsonify(categoria.to_dict())

@categoria_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def deletar_categoria(id: int):
    if not CategoriaRepository.deletar_por_id_e_usuario(id, current_user.id):
        abort(HTTPStatus.NOT_FOUND)
    return '', HTTPStatus.NO_CONTENT