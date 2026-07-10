import os

import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture()
def app():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(name="Admin", email="admin@example.com", role="admin")
        admin.set_password("password123")
        viewer = User(name="Viewer", email="viewer@example.com", role="viewer")
        viewer.set_password("password123")
        db.session.add_all([admin, viewer])
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email):
    return client.post("/auth/login", data={"email": email, "password": "password123"}, follow_redirects=True)


def test_dashboard_requires_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_viewer_can_open_dashboard_but_cannot_manage_rooms(client):
    login(client, "viewer@example.com")

    dashboard = client.get("/")
    rooms = client.get("/rooms")

    assert dashboard.status_code == 200
    assert rooms.status_code == 403


def test_dashboard_hides_optional_integration_missing_env_details(client, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("NEXT_PUBLIC_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("FIREBASE_DATABASE_URL", raising=False)
    login(client, "viewer@example.com")

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Optional cloud integrations are not configured" in body
    assert "SUPABASE_URL" not in body
    assert "FIREBASE_DATABASE_URL" not in body


def test_admin_can_create_role_based_user(client):
    login(client, "admin@example.com")

    response = client.post(
        "/auth/users",
        data={
            "name": "Scheduler",
            "email": "scheduler@example.com",
            "password": "password123",
            "role": "scheduler",
            "is_active": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    with client.application.app_context():
        assert User.query.filter_by(email="scheduler@example.com", role="scheduler").one()


def test_load_dotenv_reads_supabase_key_alias(tmp_path, monkeypatch):
    from app import _load_dotenv

    env_file = tmp_path / ".env"
    env_file.write_text(
        "SUPABASE_URL=https://example.supabase.co\n"
        "SUPABASE_KEY=publishable-test-key\n"
    )
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)

    _load_dotenv(str(env_file))

    assert os.environ["SUPABASE_URL"] == "https://example.supabase.co"
    assert os.environ["SUPABASE_KEY"] == "publishable-test-key"
