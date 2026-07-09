import pytest

from app import create_app
from app.extensions import db
from app.models import Course, Lecturer, StudentGroup, User


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
        db.session.add(admin)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client):
    return client.post("/auth/login", data={"email": "admin@example.com", "password": "password123"})


def test_courses_page_explains_required_prerequisites(client):
    login(client)

    response = client.get("/courses")

    assert response.status_code == 200
    assert b"Create at least one lecturer and one student group" in response.data
    assert b"<button disabled>Save course</button>" in response.data


def test_admin_can_create_course_when_prerequisites_exist(client):
    login(client)
    with client.application.app_context():
        lecturer = Lecturer(name="Dr Ada")
        group = StudentGroup(name="CSC 400", level="400", size=45)
        db.session.add_all([lecturer, group])
        db.session.commit()
        lecturer_id = lecturer.id
        group_id = group.id

    response = client.post(
        "/courses",
        data={
            "code": " csc401 ",
            "title": "Algorithms",
            "lecturer_id": str(lecturer_id),
            "student_group_id": str(group_id),
            "expected_class_size": "45",
            "weekly_contact_hours": "2",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Course saved." in response.data
    with client.application.app_context():
        course = Course.query.filter_by(code="CSC401").one()
        assert course.title == "Algorithms"
        assert course.lecturer_id == lecturer_id
        assert course.student_group_id == group_id


def test_course_creation_rejects_duplicate_code(client):
    login(client)
    with client.application.app_context():
        lecturer = Lecturer(name="Dr Ada")
        group = StudentGroup(name="CSC 400", level="400", size=45)
        db.session.add_all([lecturer, group])
        db.session.commit()
        db.session.add(
            Course(
                code="CSC401",
                title="Algorithms",
                lecturer_id=lecturer.id,
                student_group_id=group.id,
                expected_class_size=45,
                weekly_contact_hours=2,
            )
        )
        db.session.commit()
        lecturer_id = lecturer.id
        group_id = group.id

    response = client.post(
        "/courses",
        data={
            "code": "csc401",
            "title": "Algorithms II",
            "lecturer_id": str(lecturer_id),
            "student_group_id": str(group_id),
            "expected_class_size": "45",
            "weekly_contact_hours": "2",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Course code CSC401 already exists." in response.data
    with client.application.app_context():
        assert Course.query.filter_by(code="CSC401").count() == 1
