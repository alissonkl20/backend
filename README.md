(![dashprod-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/1f21cf18-f4ee-4bf4-b682-59fdc42a0e06)
)

Sistema de Controle de Estoque com Flask
https://img.shields.io/badge/Flask-2.3.3-green.svg
https://img.shields.io/badge/Python-3.8%252B-blue.svg
https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/Deployed%2520on-Render-5c5c5c.svg

Este projeto é um sistema de controle de estoque desenvolvido com Flask (backend) e HTML/CSS (frontend) seguindo o padrão MVC (Model-View-Controller). A aplicação permite gerenciar categorias e produtos, com um cardápio que renderiza as categorias e seus respectivos produtos.

📋 Funcionalidades
🗂️ Gestão de Categorias
Criar novas categorias

Visualizar todas as categorias existentes

Editar informações das categorias

Excluir categorias (com verificação de produtos associados)

📦 Gestão de Produtos
Adicionar novos produtos associados a categorias

Visualizar lista de produtos com informações detalhadas

Editar informações dos produtos

Excluir produtos

Controle de estoque (quantidade disponível)

🖥️ Cardápio/Catálogo
Visualização organizada por categorias

Apresentação dos produtos de forma atrativa

Interface responsiva para diferentes dispositivos

🛠️ Tecnologias Utilizadas
Backend: Flask (Python)

Frontend: HTML5, CSS3

Padrão de Arquitetura: MVC (Model-View-Controller)

Banco de Dados: SQLite (ou outro conforme configuração)

Hospedagem: Render

Versionamento: Git

📁 Estrutura do Projeto
text
projeto-estoque-flask/
│
├── app.py                 # Arquivo principal da aplicação Flask
├── requirements.txt       # Dependências do projeto
├── Procfile              # Configuração para deploy no Render
├── .gitignore            # Arquivos a serem ignorados pelo Git
│
├── models/               # Pasta dos modelos (Model)
│   ├── __init__.py
│   ├── database.py       # Configuração e modelos do banco de dados
│   ├── categoria.py      # Modelo de Categoria
│   └── produto.py        # Modelo de Produto
│
├── controllers/          # Pasta dos controladores (Controller)
│   ├── __init__.py
│   ├── categoria_controller.py  # Controlador para categorias
│   └── produto_controller.py    # Controlador para produtos
│
├── views/                # Pasta das visualizações (View)
│   ├── templates/        # Templates HTML
│   │   ├── base.html     # Template base
│   │   ├── index.html    # Página inicial
│   │   ├── categorias/   # Templates relacionados a categorias
│   │   └── produtos/     # Templates relacionados a produtos
│   │
│   └── static/           # Arquivos estáticos
│       ├── css/
│       │   └── style.css # Estilos CSS
│       ├── js/
│       └── images/
│
└── README.md             # Este arquivo de documentação
🚀 Configuração e Instalação
Pré-requisitos
Python 3.8 ou superior

Pip (gerenciador de pacotes do Python)

Git

Passos para execução local
Clone o repositório:

bash
git clone <url-do-repositorio>
cd projeto-estoque-flask
Crie um ambiente virtual (recomendado):

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
python app.py
Acesse no navegador:

text
http://localhost:5000
🌐 Deploy no Render
Pré-requisitos
Conta no Render

Repositório Git do projeto

Passos para deploy
Conecte seu repositório Git ao Render

Configure as seguintes variáveis de ambiente (se necessário):

PYTHON_VERSION: 3.8.0 (ou superior)

O Render detectará automaticamente o requirements.txt e o Procfile

Faça o deploy - o Render construirá e hospedará sua aplicação automaticamente

🏗️ Estrutura MVC Explicada
Model (Modelos)
Responsável pela representação dos dados e lógica de negócio

Classes: Categoria, Produto

Interage com o banco de dados

View (Visualização)
Templates HTML para renderização da interface

Arquivos estáticos (CSS, JS, imagens)

Apresenta os dados para o usuário final

Controller (Controlador)
Intermediário entre Model e View

Processa requisições HTTP

Implementa a lógica da aplicação

Controladores: CategoriaController, ProdutoController

🔌 Exemplos de Uso da API
Categorias
GET /categorias - Lista todas as categorias

POST /categoria - Cria uma nova categoria

PUT /categoria/<id> - Atualiza uma categoria

DELETE /categoria/<id> - Exclui uma categoria

Produtos
GET /produtos - Lista todos os produtos

POST /produto - Adiciona um novo produto

PUT /produto/<id> - Atualiza um produto

DELETE /produto/<id> - Exclui um produto

🎨 Personalização
Para personalizar o sistema, você pode:

Modificar o esquema do banco de dados em models/database.py

Adicionar novos campos aos modelos existentes

Criar novos templates na pasta views/templates/

Adicionar estilos personalizados em views/static/css/style.css

Implementar novas funcionalidades seguindo o padrão MVC

❓ Troubleshooting
Problemas Comuns
Erro de importação: Verifique se todas as dependências estão instaladas

Problemas de banco de dados: Execute novamente a inicialização do banco

Erro no deploy: Verifique os logs no Render para detalhes

Obtendo Ajuda
Se encontrar problemas:

Verifique a documentação do Flask

Consulte os logs de erro da aplicação

Verifique se todas as variáveis de ambiente estão configuradas corretamente

🔮 Próximas Melhorias Possíveis
Implementar autenticação de usuários

Adicionar sistema de permissões

Criar relatórios de estoque

Adicionar busca e filtros avançados

Implementar upload de imagens para produtos

Criar API RESTful para integração com outros sistemas

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

Desenvolvido com ❤️ usando Flask e hospedado no Render.

