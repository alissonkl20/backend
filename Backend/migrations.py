from flask_migrate import Migrate
from extensions import db
from Main import app

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        migrate.init_app(app, db)
        print("✅ Migrations inicializadas!")