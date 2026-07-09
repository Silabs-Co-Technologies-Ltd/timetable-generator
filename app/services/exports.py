from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Timetable


def build_timetable_pdf(timetable: Timetable) -> bytes:
    """Render a timetable and its entries as a PDF document."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"{timetable.term} — {timetable.status.title()}", styles["Title"]),
        Paragraph(f"Generated: {timetable.generated_at:%Y-%m-%d %H:%M UTC}", styles["Normal"]),
        Spacer(1, 12),
    ]
    if timetable.conflict_summary:
        elements.extend(
            [
                Paragraph("Scheduling notes", styles["Heading2"]),
                Paragraph(timetable.conflict_summary.replace("\n", "<br/>"), styles["BodyText"]),
                Spacer(1, 12),
            ]
        )

    rows = [["Day", "Time", "Course", "Lecturer", "Room", "Group"]]
    for entry in sorted(
        timetable.entries,
        key=lambda item: (item.timeslot.day, item.timeslot.start_time, item.course.code),
    ):
        rows.append(
            [
                entry.timeslot.day,
                entry.timeslot.label,
                f"{entry.course.code} — {entry.course.title}",
                entry.lecturer.name,
                entry.room.code,
                entry.student_group.name,
            ]
        )
    if len(rows) == 1:
        rows.append(["No scheduled entries", "", "", "", "", ""])

    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ]
        )
    )
    elements.append(table)
    document.build(elements)
    return buffer.getvalue()
