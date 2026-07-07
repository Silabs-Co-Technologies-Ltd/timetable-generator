from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from app.extensions import db
from app.routes import register_blueprints


def _default_database_uri(app: Flask) -> str:
    """Return a writable SQLite URI for local and serverless deployments."""
    configured_uri = os.getenv("DATABASE_URL")
    if configured_uri:
        return configured_uri

    if os.getenv("VERCEL"):
        return "sqlite:////tmp/timetable.sqlite"

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    return "sqlite:///timetable.sqlite"


def create_app(config_object: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=_default_database_uri(app),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app
