# Documentação do Sistema de Controle de Estoque

## 🎥 Demonstração Rápida (40 segundos)

![rend-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/6c5e5501-644e-499d-80a7-b457c8e3eb07)


*GIF mostrando as principais funcionalidades do sistema*

## 📋 Visão Geral
Este projeto é um sistema completo de controle de estoque desenvolvido com Flask implementando o padrão MVC (Model-View-Controller). A aplicação permite gerenciar categorias e produtos, com autenticação de usuários via Google OAuth e interface responsiva.

🚀 Funcionalidades Principais
✅ Autenticação de usuários com Google OAuth

✅ Gestão completa de categorias

✅ Controle de produtos com associação a categorias

✅ Dashboard interativo

✅ Cardápio/catálogo organizado por categorias

✅ Interface responsiva

🛠️ Tecnologias Utilizadas
Backend: Flask (Python)

Frontend: HTML5, CSS3, JavaScript

Autenticação: Flask-Login, OAuth (Google)

Banco de Dados: SQLAlchemy (SQLite/PostgreSQL)

Hospedagem: Render

Outras: Flask-Bcrypt, Flask-SQLAlchemy, python-dotenv

📁 Estrutura do Projeto
text
projeto-estoque-flask/
│
├── main.py                 # Arquivo principal da aplicação
├── requirements.txt        # Dependências do projeto
├── Procfile               # Configuração para deploy no Render
├── .env                   # Variáveis de ambiente (local)
├── .gitignore            # Arquivos ignorados pelo Git
│
├── controller/            # Controladores (Blueprints)
│   ├── __init__.py
│   ├── CategoriaController.py
│   └── ProdutoController.py
│
├── model/                 # Modelos de dados
│   ├── __init__.py
│   ├── UserModel.py
│   ├── CategoriaModel.py
│   └── ProdutoModel.py
│
├── repository/            # Camada de repositório
│   └── CategoriaRepository.py
│
├── extensions.py          # Inicialização de extensões Flask
├── main_routes.py         # Rotas principais e autenticação
│
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── cardapio.html
│   ├── categorias.html
│   ├── categoria_form.html
│   └── create_product.html
│
└── static/                # Arquivos estáticos
    ├── css/
    ├── js/
    └── images/
🔧 Configuração e Instalação
Pré-requisitos
Python 3.8+

Conta no Google Developers para OAuth

Conta no Render para deploy

Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto:

env
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=sqlite:///database.db
GOOGLE_CLIENT_ID=seu_google_client_id
GOOGLE_CLIENT_SECRET=seu_google_client_secret
RENDER=false  # Definir como true apenas no Render
Instalação Local
Clone o repositório:

bash
git clone <url-do-repositorio>
cd projeto-estoque-flask
Crie um ambiente virtual:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
Instale as dependências:

bash
pip install -r requirements.txt
Execute a aplicação:

bash
python main.py
Acesse: http://localhost:5000

🌐 Deploy no Render
Conecte seu repositório ao Render

Configure as variáveis de ambiente no painel do Render:

SECRET_KEY: Gere uma chave secreta

DATABASE_URL: URL do banco de dados PostgreSQL (fornecida pelo Render)

GOOGLE_CLIENT_ID: Seu Client ID do Google

GOOGLE_CLIENT_SECRET: Seu Client Secret do Google

RENDER: true

O Render detectará automaticamente as configurações e fará o deploy

🔐 Autenticação com Google OAuth
O sistema implementa autenticação segura usando Google OAuth 2.0:

Configure um projeto no Google Cloud Console

Adicione as URIs de redirecionamento:

Desenvolvimento: http://localhost:5000/login/google/callback

Produção: https://seu-app.onrender.com/login/google/callback

Obtenha as credenciais (Client ID e Client Secret)

🗃️ Estrutura do Banco de Dados
Tabelas Principais:
usuarios: Informações dos usuários (com suporte a login Google)

categorias: Categorias de produtos (relacionadas aos usuários)

produtos: Produtos do estoque (relacionados a categorias e usuários)

📊 API e Rotas Principais
Autenticação:
GET /login - Página de login

GET /login/google - Iniciar autenticação Google

GET /login/google/callback - Callback do Google OAuth

GET /logout - Logout do usuário

Dashboard e Gerenciamento:
GET / ou GET /dashboard - Dashboard principal

GET /cardapio - Visualização do cardápio

GET /categorias - Listagem de categorias

CRUD Categorias:
GET /create_categoria - Formulário de criação

POST /create_categoria - Criar categoria

GET /edit_categoria/<id> - Formulário de edição

POST /edit_categoria/<id> - Editar categoria

POST /delete_categoria/<id> - Excluir categoria

Produtos:
GET /create_product - Formulário de criação de produto

🎨 Personalização
Adicionar Novos Campos aos Modelos:
Edite os arquivos na pasta model/ e execute migração do banco.

Modificar Templates:
Os templates HTML estão na pasta templates/.

Estilos CSS:
Edite os arquivos na pasta static/css/.

❓ Solução de Problemas
Erros Comuns:
Erro de importação: Verifique se todas as dependências estão instaladas

Problemas de banco: Execute db.create_all() no contexto da aplicação

Erro OAuth: Verifique as credenciais do Google e URIs de redirecionamento

Logs:
Em desenvolvimento: Os erros são exibidos no terminal

No Render: Acesse os logs pelo painel do Render

🔮 Próximas Melhorias
Sistema de permissões e roles

Relatórios e analytics

Upload de imagens para produtos

API RESTful para integração

Sistema de pedidos e vendas

Notificações e alertas de estoque

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

Desenvolvido com ❤️ usando Flask e hospedado no Render.
