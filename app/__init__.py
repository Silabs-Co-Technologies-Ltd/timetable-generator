from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from app.extensions import db
from app.models import User
from app.routes import register_blueprints


def _load_dotenv(path: str = ".env") -> None:
    """Load simple KEY=VALUE pairs from a local .env file when present."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


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
    _load_dotenv()

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
        if User.query.count() == 0:
            admin = User(
                name=os.getenv("INITIAL_ADMIN_NAME", "System Administrator"),
                email=os.getenv("INITIAL_ADMIN_EMAIL", "admin@example.com"),
                role="admin",
            )
            admin.set_password(os.getenv("INITIAL_ADMIN_PASSWORD", "change-me-now"))
            db.session.add(admin)
            db.session.commit()

    return app
