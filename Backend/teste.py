# test_relationships.py
from _aix_support import create_app
from extensions import db
from model.UserModel import UserModel
from model.CategoriaModel import CategoriaModel
from model.ProdutoModel import ProdutoModel

app = create_app()

with app.app_context():
    # Criar usuário de teste
    usuario = UserModel(
        nome="Teste User",
        email="teste@email.com",
        senha="hashed_password"
    )
    
    db.session.add(usuario)
    db.session.commit()
    
    # Criar categoria para o usuário
    categoria = CategoriaModel(
        nome="Bebidas",
        descricao="Bebidas diversas",
        usuario_id=usuario.id
    )
    
    db.session.add(categoria)
    db.session.commit()
    
    # Criar produto para a categoria do usuário
    produto = ProdutoModel(
        nome="Coca-Cola",
        preco=5.50,
        categoria_id=categoria.id,
        usuario_id=usuario.id
    )
    
    db.session.add(produto)
    db.session.commit()
    
    # Testar relacionamentos
    print("✅ Usuário:", usuario.nome)
    print("✅ Categorias do usuário:", len(usuario.categorias))
    print("✅ Produtos do usuário:", len(usuario.produtos))
    print("✅ Produtos da categoria:", len(categoria.produtos))
    print("✅ Categoria do produto:", produto.categoria.nome)
    print("✅ Usuário do produto:", produto.usuario_id)