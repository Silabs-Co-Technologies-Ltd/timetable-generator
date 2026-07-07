from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Course, Lecturer, Room, StudentGroup, Timetable, TimetableEntry, Timeslot
from app.services.scheduler import generate_schedule
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
    return render_template("lecturers/index.html", lecturers=Lecturer.query.order_by(Lecturer.name).all())


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
        StudentGroup(name=request.form["name"], level=request.form.get("level"), size=int(request.form["size"]))
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
        db.session.add(Timeslot(day=request.form["day"], start_time=start, end_time=end, label=request.form["label"]))
        db.session.commit()
        flash("Timeslot saved.", "success")
        return redirect(url_for("main.timeslots"))
    return render_template("timeslots/index.html", timeslots=Timeslot.query.order_by(Timeslot.day, Timeslot.start_time).all())


@bp.route("/courses", methods=["GET", "POST"])
@roles_required("admin", "scheduler")
def courses():
    if request.method == "POST":
        db.session.add(
            Course(
                code=request.form["code"],
                title=request.form["title"],
                lecturer_id=int(request.form["lecturer_id"]),
                student_group_id=int(request.form["student_group_id"]),
                expected_class_size=int(request.form["expected_class_size"]),
                weekly_contact_hours=int(request.form["weekly_contact_hours"]),
                requires_projection=bool(request.form.get("requires_projection")),
            )
        )
        db.session.commit()
        flash("Course saved.", "success")
        return redirect(url_for("main.courses"))
    return render_template(
        "courses/index.html",
        courses=Course.query.order_by(Course.code).all(),
        lecturers=Lecturer.query.order_by(Lecturer.name).all(),
        groups=StudentGroup.query.order_by(StudentGroup.name).all(),
    )


@bp.route("/timetables/generate", methods=["POST"])
@roles_required("admin", "scheduler")
def generate_timetable():
    result = generate_schedule(Course.query.all(), Room.query.all(), Timeslot.query.order_by(Timeslot.day, Timeslot.start_time).all())
    timetable = Timetable(status="complete" if result.success else "infeasible", conflict_summary="\n".join(result.messages))
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
    return redirect(url_for("main.view_timetable", timetable_id=timetable.id))


@bp.get("/timetables/<int:timetable_id>")
@login_required
def view_timetable(timetable_id: int):
    timetable = Timetable.query.get_or_404(timetable_id)
    return render_template("timetables/show.html", timetable=timetable)
