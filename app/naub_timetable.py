from __future__ import annotations

from datetime import time

NAUB_TIMETABLE_TERM = "Semester 2025/2026B Lectures Timetable"
NAUB_DAY_PAIRS: tuple[tuple[str, str], ...] = (
    ("Monday", "Tuesday"),
    ("Wednesday", "Thursday"),
    ("Friday", "Saturday"),
)
NAUB_DAYS: tuple[str, ...] = tuple(day for pair in NAUB_DAY_PAIRS for day in pair)
NAUB_VENUES: tuple[str, ...] = (
    "ARLH001",
    "ARLH002",
    "ARLH003",
    "ARLH101",
    "ARLR001",
    "SSLR101",
    "ARLR101",
    "ARLR102",
)
NAUB_TIME_PERIODS: tuple[dict[str, object], ...] = (
    {
        "label": "8:00–9:00 a.m.",
        "start": time(8, 0),
        "end": time(9, 0),
        "is_lunch": False,
    },
    {
        "label": "9:00–10:00 a.m.",
        "start": time(9, 0),
        "end": time(10, 0),
        "is_lunch": False,
    },
    {
        "label": "10:00–11:00 a.m.",
        "start": time(10, 0),
        "end": time(11, 0),
        "is_lunch": False,
    },
    {
        "label": "11:00 a.m.–12:00 p.m.",
        "start": time(11, 0),
        "end": time(12, 0),
        "is_lunch": False,
    },
    {
        "label": "12:00–1:00 p.m.",
        "start": time(12, 0),
        "end": time(13, 0),
        "is_lunch": False,
    },
    {
        "label": "1:00–2:00 p.m.",
        "start": time(13, 0),
        "end": time(14, 0),
        "is_lunch": True,
    },
    {
        "label": "2:00–3:00 p.m.",
        "start": time(14, 0),
        "end": time(15, 0),
        "is_lunch": False,
    },
    {
        "label": "3:00–4:00 p.m.",
        "start": time(15, 0),
        "end": time(16, 0),
        "is_lunch": False,
    },
    {
        "label": "4:00–5:00 p.m.",
        "start": time(16, 0),
        "end": time(17, 0),
        "is_lunch": False,
    },
    {
        "label": "5:00–6:00 p.m.",
        "start": time(17, 0),
        "end": time(18, 0),
        "is_lunch": False,
    },
)
NAUB_TEACHING_PERIODS: tuple[dict[str, object], ...] = tuple(
    period for period in NAUB_TIME_PERIODS if not period["is_lunch"]
)
NAUB_DEFAULT_ROOM_CAPACITY = 120
