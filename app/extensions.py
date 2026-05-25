from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.services.kata_loader import KataLoader

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "web.login"
login_manager.login_message = "Please log in to submit solutions."
login_manager.login_message_category = "info"

migrate = Migrate()

kata_loader = KataLoader(kata_dir="katas")  # overridden in tests
