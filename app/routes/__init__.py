from flask import Flask

from app.routes.auth import bp as auth_bp
from app.routes.main import bp as main_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
