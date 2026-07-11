from __future__ import annotations

from datetime import datetime, time, timezone

from app.extensions import db
from werkzeug.security import check_password_hash, generate_password_hash


def utc_now() -> datetime:
    """Return a timezone-naive UTC timestamp for SQLAlchemy defaults."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


USER_ROLES = ("admin", "scheduler", "viewer")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="viewer")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def can_manage_data(self) -> bool:
        return self.role in {"admin", "scheduler"}

    @property
    def can_manage_users(self) -> bool:
        return self.role == "admin"


class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True)
    courses = db.relationship("Course", back_populates="lecturer")


class StudentGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    level = db.Column(db.String(50))
    size = db.Column(db.Integer, nullable=False, default=0)
    courses = db.relationship("Course", back_populates="student_group")


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    has_projection = db.Column(db.Boolean, nullable=False, default=False)


class Timeslot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False, default=time(8, 0))
    end_time = db.Column(db.Time, nullable=False, default=time(9, 0))
    label = db.Column(db.String(80), nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    expected_class_size = db.Column(db.Integer, nullable=False, default=0)
    weekly_contact_hours = db.Column(db.Integer, nullable=False, default=1)
    requires_projection = db.Column(db.Boolean, nullable=False, default=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturer.id"), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey("student_group.id"), nullable=False)
    lecturer = db.relationship("Lecturer", back_populates="courses")
    student_group = db.relationship("StudentGroup", back_populates="courses")


class LecturerAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturer.id"), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey("timeslot.id"), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    lecturer = db.relationship("Lecturer")
    timeslot = db.relationship("Timeslot")


class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(120), nullable=False, default="Current Term")
    status = db.Column(db.String(30), nullable=False, default="draft")
    generated_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    conflict_summary = db.Column(db.Text, default="")
    entries = db.relationship(
        "TimetableEntry", back_populates="timetable", cascade="all, delete-orphan"
    )


class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey("timetable.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturer.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey("timeslot.id"), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey("student_group.id"), nullable=False)
    timetable = db.relationship("Timetable", back_populates="entries")
    course = db.relationship("Course")
    lecturer = db.relationship("Lecturer")
    room = db.relationship("Room")
    timeslot = db.relationship("Timeslot")
    student_group = db.relationship("StudentGroup")
