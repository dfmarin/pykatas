from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.services.kata_loader import KataLoader

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

kata_loader = KataLoader(kata_dir="katas")  # overridden in tests
