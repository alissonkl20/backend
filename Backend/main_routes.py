from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import inspect, text
from datetime import datetime
import secrets

from extensions import db
from model.ProdutoModel import ProdutoModel
from model.CategoriaModel import CategoriaModel
from model.UserModel import UsuarioModel
from repository.CategoriaRepository import CategoriaRepository

main_bp = Blueprint('main', __name__)

# ========== FUNÇÕES AUXILIARES ==========
def get_cardapio_data():
    try:
        produtos = ProdutoModel.query.filter_by(usuario_id=current_user.id).all()
        categorias = {}
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
        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': categorias,
            'total_produtos': len(produtos),
            'usuario': current_user.nome
        }
    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        return {'erro': 'Erro ao carregar cardápio'}

# ========== ROTAS DE AUTENTICAÇÃO ==========
@main_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@main_bp.route("/login/google")
def login_google():
    # Gerar e armazenar nonce na sessão
    nonce = secrets.token_urlsafe(16)
    session['google_auth_nonce'] = nonce
    
    redirect_uri = url_for("main.callback_google", _external=True)
    return current_app.google.authorize_redirect(redirect_uri, nonce=nonce)

@main_bp.route("/login/google/callback")
def callback_google():
    try:
        token = current_app.google.authorize_access_token()
        
        # Recuperar o nonce da sessão
        nonce = session.pop('google_auth_nonce', None)
        
        # Usar parse_id_token com nonce
        user_info = current_app.google.parse_id_token(token, nonce=nonce)
        
        email = user_info.get("email")
        name = user_info.get("name")
        google_id = user_info.get("sub")

        if not email:
            flash("Não foi possível obter email do Google.", "danger")
            return redirect(url_for("main.login"))

        user = UsuarioModel.query.filter_by(email=email).first()
        if not user:
            user = UsuarioModel(
                nome=name,
                email=email,
                senha="",  # Senha vazia para usuários Google
                google_login=True,
                google_id=google_id
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Atualizar dados se necessário
            if user.nome != name:
                user.nome = name
            if not user.google_login:
                user.google_login = True
            if not user.google_id and google_id:
                user.google_id = google_id
            db.session.commit()

        login_user(user)
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("main.dashboard"))

    except Exception as e:
        print("Erro login Google:", e)
        flash("Erro ao realizar login com Google.", "danger")
        return redirect(url_for("main.login"))

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("main.login"))

# ========== ROTAS PRINCIPAIS ==========
@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    categorias = CategoriaModel.query.filter_by(usuario_id=current_user.id).all()
    return render_template("dashboard.html", usuario=current_user, categorias=categorias)

# Rotas para categorias no blueprint principal
@main_bp.route("/create_categoria", methods=["GET", "POST"])
@login_required
def create_categoria():
    if request.method == "POST":
        # Processar o formulário de criação
        nome = request.form.get("nome")
        descricao = request.form.get("descricao", "")
        
        try:
            # Criar nova categoria
            nova_categoria = CategoriaModel(
                nome=nome,
                descricao=descricao,
                usuario_id=current_user.id
            )
            db.session.add(nova_categoria)
            db.session.commit()
            
            flash("Categoria criada com sucesso!", "success")
            return redirect(url_for("main.categorias_page"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar categoria: {str(e)}", "danger")
            return render_template("categoria_form.html", categoria=None)
    
    # GET request - mostrar formulário
    return render_template("categoria_form.html", categoria=None)

@main_bp.route("/edit_categoria/<int:id>", methods=["GET", "POST"])
@login_required
def edit_categoria(id):
    categoria = CategoriaModel.query.get_or_404(id)
    
    # Verificar se a categoria pertence ao usuário atual
    if categoria.usuario_id != current_user.id:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.categorias_page"))
    
    if request.method == "POST":
        # Processar o formulário de edição
        nome = request.form.get("nome")
        descricao = request.form.get("descricao", "")
        
        try:
            categoria.nome = nome
            categoria.descricao = descricao
            db.session.commit()
            
            flash("Categoria atualizada com sucesso!", "success")
            return redirect(url_for("main.categorias_page"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar categoria: {str(e)}", "danger")
    
    # GET request - mostrar formulário com dados atuais
    return render_template("categoria_form.html", categoria=categoria)

@main_bp.route("/delete_categoria/<int:id>", methods=["POST"])
@login_required
def delete_categoria(id):
    categoria = CategoriaModel.query.get_or_404(id)
    
    # Verificar se a categoria pertence ao usuário atual
    if categoria.usuario_id != current_user.id:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.categorias_page"))
    
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoria excluída com sucesso!", "success")
    return redirect(url_for("main.categorias_page"))

@main_bp.route("/create_product")
@login_required
def create_product():
    categorias = CategoriaModel.query.filter_by(usuario_id=current_user.id).all()
    return render_template("create_product.html", categorias=categorias)

@main_bp.route("/cardapio")
@login_required
def cardapio_html():
    try:
        dados = get_cardapio_data()
        return render_template("cardapio.html", dados=dados, usuario=current_user)
    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        flash("Erro ao carregar cardápio", "error")
        return redirect(url_for("main.dashboard"))

@main_bp.route('/categorias')
@login_required
def categorias_page():
    categorias = CategoriaRepository.listar_por_usuario(current_user.id)
    return render_template("categorias.html", categorias=categorias)