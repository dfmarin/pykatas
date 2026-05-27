from flask import Blueprint

web_bp = Blueprint("web", __name__)

# Import routes to register them with the blueprint.
from app.web import routes  # noqa: F401, E402
