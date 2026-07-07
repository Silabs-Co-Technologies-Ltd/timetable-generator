from flask import Flask

from app.routes.main import bp as main_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
