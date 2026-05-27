from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, login_manager, migrate


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(config_by_name[config_name])

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from app.web.routes import web_bp
    from app.api.routes import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # custom template filters
    @app.template_filter("truncate_words")
    def truncate_words(s: str, num: int = 20) -> str:
        words = s.split()
        if len(words) <= num:
            return s
        return " ".join(words[:num]) + "…"

    return app
