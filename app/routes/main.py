from __future__ import annotations

from datetime import datetime
from io import BytesIO

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from app.extensions import db
from app.models import Course, Lecturer, Room, StudentGroup, Timetable, TimetableEntry, Timeslot
from app.services.exports import build_timetable_pdf
from app.services.scheduler import generate_schedule
from app.services.supabase import sync_timetable_history
from app.routes.auth import login_required, roles_required

bp = Blueprint("main", __name__)


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
        latest_timetable=Timetable.query.order_by(Timetable.generated_at.desc()).first(),
    )


@bp.route("/lecturers", methods=["GET", "POST"])
@roles_required("admin", "scheduler")
def lecturers():
    if request.method == "POST":
        db.session.add(Lecturer(name=request.form["name"], email=request.form.get("email") or None))
        db.session.commit()
        flash("Lecturer saved.", "success")
        return redirect(url_for("main.lecturers"))
    return render_template(
        "lecturers/index.html", lecturers=Lecturer.query.order_by(Lecturer.name).all()
    )


@bp.route("/rooms", methods=["GET", "POST"])
@roles_required("admin", "scheduler")
def rooms():
    if request.method == "POST":
        db.session.add(
            Room(
                code=request.form["code"],
                capacity=int(request.form["capacity"]),
                has_projection=bool(request.form.get("has_projection")),
            )
        )
        db.session.commit()
        flash("Room saved.", "success")
        return redirect(url_for("main.rooms"))
    return render_template("rooms/index.html", rooms=Room.query.order_by(Room.code).all())


@bp.route("/groups", methods=["POST"])
@roles_required("admin", "scheduler")
def groups():
    db.session.add(
        StudentGroup(
            name=request.form["name"],
            level=request.form.get("level"),
            size=int(request.form["size"]),
        )
    )
    db.session.commit()
    flash("Student group saved.", "success")
    return redirect(url_for("main.courses"))


@bp.route("/timeslots", methods=["GET", "POST"])
@roles_required("admin", "scheduler")
def timeslots():
    if request.method == "POST":
        start = datetime.strptime(request.form["start_time"], "%H:%M").time()
        end = datetime.strptime(request.form["end_time"], "%H:%M").time()
        db.session.add(
            Timeslot(
                day=request.form["day"], start_time=start, end_time=end, label=request.form["label"]
            )
        )
        db.session.commit()
        flash("Timeslot saved.", "success")
        return redirect(url_for("main.timeslots"))
    return render_template(
        "timeslots/index.html",
        timeslots=Timeslot.query.order_by(Timeslot.day, Timeslot.start_time).all(),
    )


@bp.route("/courses", methods=["GET", "POST"])
@roles_required("admin", "scheduler")
def courses():
    lecturers = Lecturer.query.order_by(Lecturer.name).all()
    groups = StudentGroup.query.order_by(StudentGroup.name).all()

    if request.method == "POST":
        if not lecturers or not groups:
            flash(
                "Add at least one lecturer and one student group before saving a course.", "error"
            )
            return redirect(url_for("main.courses"))

        code = request.form.get("code", "").strip().upper()
        title = request.form.get("title", "").strip()
        lecturer_id = request.form.get("lecturer_id", type=int)
        student_group_id = request.form.get("student_group_id", type=int)
        expected_class_size = request.form.get("expected_class_size", type=int)
        weekly_contact_hours = request.form.get("weekly_contact_hours", type=int)

        selected_lecturer = db.session.get(Lecturer, lecturer_id) if lecturer_id else None
        selected_group = (
            db.session.get(StudentGroup, student_group_id) if student_group_id else None
        )
        if not code or not title or not selected_lecturer or not selected_group:
            flash(
                "Select a valid lecturer and student group, then enter the course code and title.",
                "error",
            )
            return redirect(url_for("main.courses"))
        if (
            expected_class_size is None
            or expected_class_size < 1
            or weekly_contact_hours is None
            or weekly_contact_hours < 1
        ):
            flash("Class size and weekly contact hours must be at least 1.", "error")
            return redirect(url_for("main.courses"))
        if Course.query.filter_by(code=code).first():
            flash(f"Course code {code} already exists.", "error")
            return redirect(url_for("main.courses"))

        db.session.add(
            Course(
                code=code,
                title=title,
                lecturer_id=selected_lecturer.id,
                student_group_id=selected_group.id,
                expected_class_size=expected_class_size,
                weekly_contact_hours=weekly_contact_hours,
                requires_projection=bool(request.form.get("requires_projection")),
            )
        )
        db.session.commit()
        flash("Course saved.", "success")
        return redirect(url_for("main.courses"))
    return render_template(
        "courses/index.html",
        courses=Course.query.order_by(Course.code).all(),
        lecturers=lecturers,
        groups=groups,
    )


@bp.route("/timetables/generate", methods=["POST"])
@roles_required("admin", "scheduler")
def generate_timetable():
    result = generate_schedule(
        Course.query.all(),
        Room.query.all(),
        Timeslot.query.order_by(Timeslot.day, Timeslot.start_time).all(),
    )
    timetable = Timetable(
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
    synced, sync_message = sync_timetable_history(timetable)
    flash(result.messages[0], "success" if result.success else "error")
    flash(sync_message, "success" if synced else "warning")
    return redirect(url_for("main.view_timetable", timetable_id=timetable.id))


@bp.get("/timetables/<int:timetable_id>")
@login_required
def view_timetable(timetable_id: int):
    timetable = Timetable.query.get_or_404(timetable_id)
    return render_template("timetables/show.html", timetable=timetable)


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
