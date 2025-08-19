from Main import create_app
from extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")
    print("✅ Banco de dados pronto para uso!")