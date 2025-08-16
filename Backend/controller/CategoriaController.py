from flask import Blueprint, request, jsonify, abort
from http import HTTPStatus
from typing import List
from extensions import db
from model.CategoriaModel import CategoriaModel
from repository.CategoriaRepository import CategoriaRepository

categoria_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')

@categoria_bp.route('/', methods=['GET'])
def listar_categorias():
    categorias: List[CategoriaModel] = CategoriaRepository.listar_todos()  # Método estático
    return jsonify([categoria.to_dict() for categoria in categorias])

@categoria_bp.route('/', methods=['POST'])
def criar_categoria():
    data = request.get_json()
    if not data or 'nome' not in data:
        abort(HTTPStatus.BAD_REQUEST, description="Nome da categoria é obrigatório")

    if CategoriaRepository.existe_por_nome(data['nome']):  # Método estático
        abort(HTTPStatus.CONFLICT, description="Categoria já existe")
    
    categoria = CategoriaModel(nome=data['nome'])
    CategoriaRepository.salvar(categoria)  # Método estático
    return jsonify(categoria.to_dict()), HTTPStatus.CREATED

@categoria_bp.route('/<int:id>', methods=['GET'])
def buscar_categoria(id: int):
    categoria = CategoriaRepository.buscar_por_id(id)  # Método estático
    if not categoria:
        abort(HTTPStatus.NOT_FOUND)
    return jsonify(categoria.to_dict())

@categoria_bp.route('/<int:id>', methods=['DELETE'])
def deletar_categoria(id: int):
    if not CategoriaRepository.deletar_por_id(id):  # Método estático
        abort(HTTPStatus.NOT_FOUND)
    return '', HTTPStatus.NO_CONTENT