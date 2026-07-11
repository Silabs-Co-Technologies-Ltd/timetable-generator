from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from app.extensions import db
from app.models import Room, Timeslot, User
from app.naub_timetable import (
    NAUB_DEFAULT_ROOM_CAPACITY,
    NAUB_TEACHING_PERIODS,
    NAUB_TIMETABLE_TERM,
    NAUB_VENUES,
    NAUB_DAYS,
)
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
    """Return the persistent SQLite database URI used for all application data."""
    configured_path = os.getenv("SQLITE_DATABASE_PATH", "").strip()
    if configured_path:
        path = Path(configured_path).expanduser()
        if not path.is_absolute():
            path = Path(app.instance_path) / path
    else:
        path = Path(app.instance_path) / "timetable.sqlite3"

    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


def _seed_naub_structure() -> None:
    """Ensure the fixed NAUB timetable venues and teaching periods exist."""
    for venue in NAUB_VENUES:
        if not Room.query.filter_by(code=venue).first():
            db.session.add(
                Room(
                    code=venue, capacity=NAUB_DEFAULT_ROOM_CAPACITY, has_projection=True
                )
            )

    for day in NAUB_DAYS:
        for period in NAUB_TEACHING_PERIODS:
            exists = Timeslot.query.filter_by(
                day=day, start_time=period["start"], end_time=period["end"]
            ).first()
            if not exists:
                db.session.add(
                    Timeslot(
                        day=day,
                        start_time=period["start"],
                        end_time=period["end"],
                        label=str(period["label"]),
                    )
                )
    db.session.commit()


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
        _seed_naub_structure()

    return app
