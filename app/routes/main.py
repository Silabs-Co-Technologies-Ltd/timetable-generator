from __future__ import annotations

from io import BytesIO

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import (
    Course,
    Lecturer,
    Room,
    StudentGroup,
    Timetable,
    TimetableEntry,
    Timeslot,
)
from app.naub_timetable import (
    NAUB_DAY_PAIRS,
    NAUB_DAYS,
    NAUB_TIME_PERIODS,
    NAUB_TIMETABLE_TERM,
    NAUB_VENUES,
)
from app.routes.auth import login_required, roles_required
from app.services.exports import build_timetable_pdf
from app.services.scheduler import generate_schedule

EDITABLE_COURSE_FIELDS = (
    "code",
    "title",
    "unit",
    "status",
    "lecture_hours",
    "practical_hours",
    "semester",
    "expected_class_size",
    "weekly_contact_hours",
    "requires_projection",
    "lecturer_id",
    "student_group_id",
)

bp = Blueprint("main", __name__)


def _naub_timeslot_sort_key(timeslot: Timeslot) -> tuple[int, object]:
    try:
        day_index = NAUB_DAYS.index(timeslot.day)
    except ValueError:
        day_index = len(NAUB_DAYS)
    return day_index, timeslot.start_time


def _positive_int(name: str, default: int | None = None) -> int | None:
    value = request.form.get(name, type=int)
    return default if value is None else value


def _course_form_values() -> dict[str, object]:
    lecture_hours = _positive_int("lecture_hours", 0) or 0
    practical_hours = _positive_int("practical_hours", 0) or 0
    weekly_contact_hours = _positive_int("weekly_contact_hours")
    if weekly_contact_hours is None:
        weekly_contact_hours = max(1, round((lecture_hours + practical_hours) / 15))
    return {
        "code": request.form.get("code", "").strip().upper(),
        "title": request.form.get("title", "").strip(),
        "unit": _positive_int("unit", 1) or 1,
        "status": request.form.get("status", "C").strip().upper() or "C",
        "lecture_hours": lecture_hours,
        "practical_hours": practical_hours,
        "semester": request.form.get("semester", "1").strip() or "1",
        "lecturer_id": request.form.get("lecturer_id", type=int),
        "student_group_id": request.form.get("student_group_id", type=int),
        "expected_class_size": _positive_int("expected_class_size"),
        "weekly_contact_hours": weekly_contact_hours,
        "requires_projection": bool(request.form.get("requires_projection")),
    }


@bp.get("/")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        counts={
            "courses": Course.query.count(),
            "lecturers": Lecturer.query.count(),
            "rooms": Room.query.count(),
            "timeslots": Timeslot.query.count(),
        },
        latest_timetable=Timetable.query.order_by(
            Timetable.generated_at.desc()
        ).first(),
        timetable_history=Timetable.query.order_by(Timetable.generated_at.desc())
        .limit(5)
        .all(),
        timetable_term=NAUB_TIMETABLE_TERM,
    )


@bp.route("/lecturers", methods=["GET", "POST"])
@roles_required("admin")
def lecturers():
    if request.method == "POST":
        lecturer_id = request.form.get("lecturer_id", type=int)
        lecturer = db.session.get(Lecturer, lecturer_id) if lecturer_id else Lecturer()
        if lecturer is None:
            flash("Lecturer not found.", "error")
            return redirect(url_for("main.lecturers"))
        lecturer.name = request.form["name"].strip()
        lecturer.email = (request.form.get("email") or "").strip() or None
        db.session.add(lecturer)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("A lecturer with that email already exists.", "error")
            return redirect(url_for("main.lecturers"))
        flash("Lecturer saved.", "success")
        return redirect(url_for("main.lecturers"))
    return render_template(
        "lecturers/index.html", lecturers=Lecturer.query.order_by(Lecturer.name).all()
    )


@bp.post("/lecturers/<int:lecturer_id>/delete")
@roles_required("admin")
def delete_lecturer(lecturer_id: int):
    lecturer = Lecturer.query.get_or_404(lecturer_id)
    db.session.delete(lecturer)
    db.session.commit()
    flash("Lecturer deleted.", "success")
    return redirect(url_for("main.lecturers"))


@bp.route("/rooms", methods=["GET", "POST"])
@roles_required("admin")
def rooms():
    if request.method == "POST":
        room_id = request.form.get("room_id", type=int)
        room = db.session.get(Room, room_id) if room_id else Room()
        if room is None:
            flash("Room not found.", "error")
            return redirect(url_for("main.rooms"))
        room.code = request.form["code"].strip().upper()
        room.capacity = int(request.form["capacity"])
        room.has_projection = bool(request.form.get("has_projection"))
        db.session.add(room)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("A room with that code already exists.", "error")
            return redirect(url_for("main.rooms"))
        flash("Room saved.", "success")
        return redirect(url_for("main.rooms"))
    return render_template(
        "rooms/index.html", rooms=Room.query.order_by(Room.code).all()
    )


@bp.post("/rooms/<int:room_id>/delete")
@roles_required("admin")
def delete_room(room_id: int):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted.", "success")
    return redirect(url_for("main.rooms"))


@bp.route("/groups", methods=["POST"])
@roles_required("admin")
def groups():
    group_id = request.form.get("group_id", type=int)
    group = db.session.get(StudentGroup, group_id) if group_id else StudentGroup()
    if group is None:
        flash("Student group not found.", "error")
        return redirect(url_for("main.courses"))
    group.name = request.form["name"].strip()
    group.level = request.form.get("level")
    group.size = int(request.form["size"])
    db.session.add(group)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("A student group with that name already exists.", "error")
        return redirect(url_for("main.courses"))
    flash("Student group saved.", "success")
    return redirect(url_for("main.courses"))


@bp.post("/groups/<int:group_id>/delete")
@roles_required("admin")
def delete_group(group_id: int):
    group = StudentGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Student group deleted.", "success")
    return redirect(url_for("main.courses"))


@bp.route("/timeslots", methods=["GET", "POST"])
@roles_required("admin", "scheduler")
def timeslots():
    if request.method == "POST":
        flash("NAUB timetable periods are fixed for Semester 2025/2026B.", "error")
        return redirect(url_for("main.timeslots"))
    return render_template(
        "timeslots/index.html",
        timeslots=sorted(Timeslot.query.all(), key=_naub_timeslot_sort_key),
    )


@bp.route("/courses", methods=["GET", "POST"])
@roles_required("admin")
def courses():
    lecturers = Lecturer.query.order_by(Lecturer.name).all()
    groups = StudentGroup.query.order_by(StudentGroup.name).all()

    if request.method == "POST":
        if not lecturers or not groups:
            flash(
                "Add at least one lecturer and one student group before saving a course.",
                "error",
            )
            return redirect(url_for("main.courses"))

        values = _course_form_values()
        selected_lecturer = db.session.get(Lecturer, values["lecturer_id"])
        selected_group = db.session.get(StudentGroup, values["student_group_id"])
        if (
            not values["code"]
            or not values["title"]
            or not selected_lecturer
            or not selected_group
        ):
            flash(
                "Select a valid lecturer and student group, then enter the course code and title.",
                "error",
            )
            return redirect(url_for("main.courses"))
        if (
            values["expected_class_size"] is None
            or values["expected_class_size"] < 1
            or values["weekly_contact_hours"] < 1
        ):
            flash("Class size and weekly contact hours must be at least 1.", "error")
            return redirect(url_for("main.courses"))

        course_id = request.form.get("course_id", type=int)
        course = db.session.get(Course, course_id) if course_id else Course()
        if course is None:
            flash("Course not found.", "error")
            return redirect(url_for("main.courses"))
        duplicate = Course.query.filter(
            Course.code == values["code"], Course.id != (course.id or 0)
        ).first()
        if duplicate:
            flash(f"Course code {values['code']} already exists.", "error")
            return redirect(url_for("main.courses"))
        for field in EDITABLE_COURSE_FIELDS:
            setattr(course, field, values[field])
        db.session.add(course)
        db.session.commit()
        flash("Course saved.", "success")
        return redirect(url_for("main.courses"))
    return render_template(
        "courses/index.html",
        courses=Course.query.order_by(Course.code).all(),
        lecturers=lecturers,
        groups=groups,
    )


@bp.post("/courses/<int:course_id>/delete")
@roles_required("admin")
def delete_course(course_id: int):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted.", "success")
    return redirect(url_for("main.courses"))


@bp.route("/timetables/generate", methods=["POST"])
@roles_required("admin", "scheduler")
def generate_timetable():
    result = generate_schedule(
        Course.query.all(),
        Room.query.all(),
        sorted(Timeslot.query.all(), key=_naub_timeslot_sort_key),
    )
    timetable = Timetable(
        term=NAUB_TIMETABLE_TERM,
        status="complete" if result.success else "infeasible",
        conflict_summary="\n".join(result.messages),
    )
    db.session.add(timetable)
    db.session.flush()
    for item in result.assignments:
        db.session.add(
            TimetableEntry(
                timetable_id=timetable.id,
                course_id=item.course.id,
                lecturer_id=item.course.lecturer_id,
                room_id=item.room.id,
                timeslot_id=item.timeslot.id,
                student_group_id=item.course.student_group_id,
            )
        )
    db.session.commit()
    flash(result.messages[0], "success" if result.success else "error")
    flash("Timetable saved to the persistent SQLite database.", "success")
    return redirect(url_for("main.view_timetable", timetable_id=timetable.id))


@bp.get("/timetables")
@login_required
def timetable_history():
    local_history = Timetable.query.order_by(Timetable.generated_at.desc()).all()
    return render_template("timetables/index.html", local_history=local_history)


@bp.get("/timetables/<int:timetable_id>")
@login_required
def view_timetable(timetable_id: int):
    timetable = Timetable.query.get_or_404(timetable_id)
    return render_template(
        "timetables/show.html",
        timetable=timetable,
        day_pairs=NAUB_DAY_PAIRS,
        time_periods=NAUB_TIME_PERIODS,
        venue_codes=NAUB_VENUES,
    )


@bp.get("/timetables/<int:timetable_id>/pdf")
@login_required
def export_timetable_pdf(timetable_id: int):
    timetable = Timetable.query.get_or_404(timetable_id)
    pdf = build_timetable_pdf(timetable)
    filename = f"timetable-{timetable.id}.pdf"
    return send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
