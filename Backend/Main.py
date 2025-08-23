from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime

# Blueprints
from controller.CategoriaController import categoria_bp
from controller.ProdutoController import produto_bp

# Extensões
from extensions import db

# Modelos
from model.ProdutoModel import ProdutoModel
from model.CategoriaModel import CategoriaModel
from model.UserModel import UsuarioModel

# Carrega variáveis do .env apenas em desenvolvimento
if os.environ.get("RENDER") is None:
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

# Cria a instância do Flask
app = Flask(__name__, template_folder="templates")

# Configuração de segurança
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-padrao-mude-isso")

# Configuração do banco
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa extensões
db.init_app(app)
CORS(app)
Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return UsuarioModel.query.get(int(user_id))

# DEBUG: Verificar se a pasta templates existe
template_path = Path(__file__).parent / "templates"
print(f"📁 Caminho dos templates: {template_path}")

if template_path.exists():
    templates = list(template_path.glob("*.html"))
    print(f"📄 Templates encontrados: {[t.name for t in templates]}")
else:
    print("❌ Pasta templates não encontrada!")
    template_path.mkdir(exist_ok=True)
    print("✅ Pasta templates criada")

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas/verificadas!")
    
    # DEBUG: Verificar usuários no banco
    users = UsuarioModel.query.all()
    print(f"📊 Usuários no banco: {len(users)}")
    for user in users:
        print(f"👤 Usuário: {user.email}")

# Registra os blueprints (SEM url_prefix adicional)
app.register_blueprint(categoria_bp)
app.register_blueprint(produto_bp)

# Rotas de autenticação
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password_sha256 = request.form.get("password")  # já vem SHA-256 do frontend

        # DEBUG: Log dos dados recebidos
        print(f"🔐 Tentativa de login - Email: {email}")
        print(f"🔐 Senha SHA-256 recebida: {password_sha256}")

        user = UsuarioModel.query.filter_by(email=email).first()
        print(f"👤 Usuário encontrado: {user is not None}")

        # Comparar bcrypt(SHA-256) com hash do banco
        if user:
            print(f"🔑 Hash do banco: {user.senha}")
            password_match = bcrypt.check_password_hash(user.senha, password_sha256)
            print(f"✅ Verificação bcrypt: {password_match}")
            
            if password_match:
                login_user(user)
                next_page = request.args.get("next")
                flash("Login realizado com sucesso!", "success")
                print("🎉 Login bem-sucedido! Redirecionando...")
                return redirect(next_page or url_for("dashboard"))
        
        # Se chegou aqui, o login falhou
        flash("Login falhou. Verifique seu email e senha.", "danger")
        print("❌ Login falhou")

    return render_template("login.html")

@app.route("/cadastro_usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha_sha256 = request.form.get("password")  # já vem SHA-256
        confirmar_sha256 = request.form.get("confirm_password")

        if senha_sha256 != confirmar_sha256:
            flash("As senhas não coincidem.", "danger")
            return render_template("cadastro.html")

        if UsuarioModel.query.filter_by(email=email).first():
            flash("Este email já está em uso.", "danger")
            return render_template("cadastro.html")

        # Salvar bcrypt(SHA-256)
        hashed_password = bcrypt.generate_password_hash(senha_sha256).decode("utf-8")
        novo_usuario = UsuarioModel(nome=nome, email=email, senha=hashed_password)

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("login"))

# Função para obter dados do cardápio
def get_cardapio_data():
    try:
        produtos = ProdutoModel.query.filter_by(usuario_id=current_user.id).all()
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

        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': categorias,
            'total_produtos': total_produtos,
            'usuario': current_user.nome
        }

    except Exception as e:
        print(f"❌ Erro ao carregar cardápio: {str(e)}")
        return {
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': {},
            'total_produtos': 0,
            'erro': f'Erro ao carregar cardápio: {str(e)}'
        }

# Rotas protegidas
@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user)

@app.route("/create_product", methods=["GET", "POST"])
@login_required
def create_product():
    if request.method == "POST":
        # TODO: lógica de criação de produto
        pass
    return render_template("create_product.html", usuario=current_user)

@app.route("/cadastro")
def cadastro_redirect():
    return redirect(url_for("create_product"))

@app.route("/cardapio")
@login_required
def cardapio_html():
    dados = get_cardapio_data()
    return render_template("cardapio.html", dados=dados, usuario=current_user)

# ========== ROTAS PARA CATEGORIAS ==========

@app.route("/categorias")
@login_required
def categorias_page():
    categorias = CategoriaModel.query.filter_by(usuario_id=current_user.id).all()
    return render_template("categorias.html", categorias=categorias, usuario=current_user)

@app.route("/create_category", methods=["GET", "POST"])
@login_required
def create_category():
    if request.method == "POST":
        try:
            nome = request.form.get("nome")
            descricao = request.form.get("descricao", "")
            
            if not nome:
                flash("Nome da categoria é obrigatório", "danger")
                return render_template("create_category.html", usuario=current_user)
            
            # Verifica se já existe categoria com mesmo nome para este usuário
            existing = CategoriaModel.query.filter_by(
                nome=nome, 
                usuario_id=current_user.id
            ).first()
            
            if existing:
                flash("Já existe uma categoria com este nome", "danger")
                return render_template("create_category.html", usuario=current_user)
            
            nova_categoria = CategoriaModel(
                nome=nome,
                descricao=descricao,
                usuario_id=current_user.id
            )
            
            db.session.add(nova_categoria)
            db.session.commit()
            
            flash("Categoria criada com sucesso!", "success")
            return redirect(url_for("categorias_page"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar categoria: {str(e)}", "danger")
            return render_template("create_category.html", usuario=current_user)
    
    return render_template("create_category.html", usuario=current_user)

@app.route("/edit_category/<int:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):
    categoria = CategoriaModel.query.filter_by(id=id, usuario_id=current_user.id).first()
    
    if not categoria:
        flash("Categoria não encontrada", "danger")
        return redirect(url_for("categorias_page"))
    
    if request.method == "POST":
        try:
            nome = request.form.get("nome")
            descricao = request.form.get("descricao", "")
            
            if not nome:
                flash("Nome da categoria é obrigatório", "danger")
                return render_template("edit_category.html", categoria=categoria, usuario=current_user)
            
            # Verifica se outra categoria com mesmo nome existe
            existing = CategoriaModel.query.filter(
                CategoriaModel.nome == nome,
                CategoriaModel.usuario_id == current_user.id,
                CategoriaModel.id != id
            ).first()
            
            if existing:
                flash("Já existe outra categoria com este nome", "danger")
                return render_template("edit_category.html", categoria=categoria, usuario=current_user)
            
            categoria.nome = nome
            categoria.descricao = descricao
            db.session.commit()
            
            flash("Categoria atualizada com sucesso!", "success")
            return redirect(url_for("categorias_page"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar categoria: {str(e)}", "danger")
            return render_template("edit_category.html", categoria=categoria, usuario=current_user)
    
    return render_template("edit_category.html", categoria=categoria, usuario=current_user)

@app.route("/delete_category/<int:id>", methods=["POST"])
@login_required
def delete_category(id):
    categoria = CategoriaModel.query.filter_by(id=id, usuario_id=current_user.id).first()
    
    if not categoria:
        flash("Categoria não encontrada", "danger")
        return redirect(url_for("categorias_page"))
    
    try:
        # Verifica se existem produtos nesta categoria
        if categoria.produtos:
            flash("Não é possível excluir categoria com produtos. Remova os produtos primeiro.", "danger")
            return redirect(url_for("categorias_page"))
        
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoria excluída com sucesso!", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir categoria: {str(e)}", "danger")
    
    return redirect(url_for("categorias_page"))

# Lista todas as rotas para debug
with app.app_context():
    print("🌐 Rotas registradas:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':  # Ignora rotas estáticas
            print(f"   {rule.rule} -> {rule.endpoint}")

# Executa o aplicativo
if __name__ == "__main__":
    print("✅ Aplicativo Flask criado com sucesso!")
    print("🌐 Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)