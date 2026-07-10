from datetime import datetime, time

from app.models import Course, Lecturer, Room, StudentGroup, Timetable, TimetableEntry, Timeslot
from app.services.exports import build_timetable_pdf
from app.services.supabase import timetable_payload


def make_timetable():
    lecturer = Lecturer(id=1, name="Dr Ada")
    group = StudentGroup(id=1, name="CS 400", size=30)
    room = Room(id=1, code="LAB1", capacity=40)
    slot = Timeslot(id=1, day="Monday", label="08:00-09:00", start_time=time(8), end_time=time(9))
    course = Course(id=1, code="CSC401", title="Algorithms", lecturer=lecturer, student_group=group)
    timetable = Timetable(
        id=7, term="Current Term", status="complete", generated_at=datetime(2026, 7, 9, 12, 0)
    )
    timetable.entries = [
        TimetableEntry(
            course=course, lecturer=lecturer, room=room, timeslot=slot, student_group=group
        )
    ]
    return timetable


def test_build_timetable_pdf_returns_pdf_bytes():
    pdf = build_timetable_pdf(make_timetable())

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_timetable_payload_serializes_history_entries():
    payload = timetable_payload(make_timetable())

    assert payload["local_id"] == 7
    assert payload["entries"][0]["course_code"] == "CSC401"
    assert payload["entries"][0]["room"] == "LAB1"


def test_fetch_history_reports_missing_supabase_configuration(monkeypatch):
    from app.services.supabase import fetch_timetable_history

    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)

    rows, message = fetch_timetable_history()

    assert rows == []
    assert message == "Supabase is not configured."


def test_firebase_connection_reports_missing_configuration(monkeypatch):
    from app.services.firebase import check_firebase_connection

    monkeypatch.delenv("FIREBASE_DATABASE_URL", raising=False)

    connected, message = check_firebase_connection()

    assert connected is False
    assert "Firebase is not configured" in message
