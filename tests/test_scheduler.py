from app.models import Course, Lecturer, Room, StudentGroup, Timeslot
from app.services.scheduler import generate_schedule


def test_generate_schedule_places_course_without_conflicts():
    lecturer = Lecturer(id=1, name="Dr Ada")
    group = StudentGroup(id=1, name="CS 400", size=30)
    course = Course(
        id=1,
        code="CSC401",
        title="Algorithms",
        lecturer_id=1,
        lecturer=lecturer,
        student_group_id=1,
        student_group=group,
        expected_class_size=30,
        weekly_contact_hours=1,
    )
    room = Room(id=1, code="LAB1", capacity=40)
    slot = Timeslot(id=1, day="Monday", label="08:00-09:00")

    result = generate_schedule([course], [room], [slot])

    assert result.success is True
    assert len(result.assignments) == 1
    assert result.assignments[0].course.code == "CSC401"


def test_generate_schedule_reports_capacity_failure():
    course = Course(
        id=1,
        code="CSC402",
        title="Databases",
        lecturer_id=1,
        student_group_id=1,
        expected_class_size=90,
        weekly_contact_hours=1,
    )
    room = Room(id=1, code="R1", capacity=20)
    slot = Timeslot(id=1, day="Tuesday", label="10:00-11:00")

    result = generate_schedule([course], [room], [slot])

    assert result.success is False
    assert "Could not place CSC402" in result.messages[0]
