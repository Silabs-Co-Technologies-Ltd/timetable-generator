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

CCMAS_DEFAULT_GROUPS: tuple[dict[str, object], ...] = (
    {"name": "B.Sc. ICT 100", "level": "100", "size": 120},
    {"name": "B.Sc. ICT 200", "level": "200", "size": 120},
    {"name": "B.Sc. ICT 300", "level": "300", "size": 120},
    {"name": "B.Sc. ICT 400", "level": "400", "size": 120},
    {"name": "B.Sc. ICT 500", "level": "500", "size": 120},
    {"name": "B.Sc. Cybersecurity 100", "level": "100", "size": 120},
    {"name": "B.Sc. Cybersecurity 200", "level": "200", "size": 120},
    {"name": "B.Sc. Cybersecurity 300", "level": "300", "size": 120},
    {"name": "B.Sc. Cybersecurity 400", "level": "400", "size": 120},
    {"name": "B.Sc. Cybersecurity 500", "level": "500", "size": 120},
)

CCMAS_DEFAULT_COURSES: tuple[dict[str, object], ...] = (
    {"code":"C-GST 111","title":"Communication in English","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-GST 112","title":"Nigerian Peoples and Culture","unit":2,"status":"C","lh":30,"ph":0,"semester":"2","group":"B.Sc. ICT 100"},
    {"code":"C-COS 101","title":"Introduction to Computing Sciences","unit":3,"status":"C","lh":30,"ph":45,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-COS 102","title":"Problem Solving","unit":3,"status":"C","lh":30,"ph":45,"semester":"2","group":"B.Sc. ICT 100"},
    {"code":"C-MTH 101","title":"Elementary Mathematics I (Algebra & Trigonometry)","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-MTH 102","title":"Elementary Mathematics II (Calculus)","unit":2,"status":"C","lh":30,"ph":0,"semester":"2","group":"B.Sc. ICT 100"},
    {"code":"C-STA 111","title":"Descriptive Statistics","unit":3,"status":"C","lh":45,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-PHY 101","title":"General Physics I (Mechanics)","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-PHY 102","title":"General Physics II (Electricity & Magnetism)","unit":2,"status":"C","lh":30,"ph":0,"semester":"2","group":"B.Sc. ICT 100"},
    {"code":"C-PHY 107","title":"General Practical Physics I","unit":1,"status":"C","lh":0,"ph":45,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-PHY 108","title":"General Practical Physics II","unit":1,"status":"C","lh":0,"ph":45,"semester":"2","group":"B.Sc. ICT 100"},
    {"code":"C-MTH 103","title":"Elementary Mathematics III (Vectors, Geometry and Dynamics)","unit":2,"status":"R","lh":30,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-STA 122","title":"Statistical Computing I","unit":3,"status":"R","lh":15,"ph":90,"semester":"2","group":"B.Sc. ICT 100"},
    {"code":"C-UI-COS 103","title":"Practical Lab I","unit":2,"status":"C","lh":0,"ph":90,"semester":"1st and 2nd","group":"B.Sc. ICT 100"},
    {"code":"C-UI-GES 107","title":"Reproductive health, sexually transmitted infections (STIs) & HIV","unit":1,"status":"R","lh":0,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-UI-GES 108","title":"Introduction to French","unit":1,"status":"R","lh":0,"ph":0,"semester":"1","group":"B.Sc. ICT 100"},
    {"code":"C-GST 212","title":"Philosophy, Logic and Human Existence","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. ICT 200"},
    {"code":"C-ENT 211","title":"Entrepreneurship and Innovation","unit":2,"status":"C","lh":30,"ph":0,"semester":"2","group":"B.Sc. ICT 200"},
    {"code":"C-IFT 211","title":"Digital Logic Design","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. ICT 200"},
    {"code":"C-COS 201","title":"Computer Programming I","unit":3,"status":"C","lh":30,"ph":45,"semester":"1","group":"B.Sc. ICT 200"},
    {"code":"C-COS 202","title":"Computer Programming II","unit":3,"status":"C","lh":30,"ph":45,"semester":"2","group":"B.Sc. ICT 200"},
    {"code":"C-CYB 201","title":"Introduction to Cybersecurity and Strategy","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. Cybersecurity 200"},
    {"code":"C-CYB 203","title":"Cybercrime, Law and Countermeasures","unit":2,"status":"C","lh":30,"ph":0,"semester":"2","group":"B.Sc. Cybersecurity 200"},
    {"code":"C-CYB 301","title":"Cryptography Techniques, Algorithms and Applications","unit":2,"status":"C","lh":15,"ph":45,"semester":"1","group":"B.Sc. Cybersecurity 300"},
    {"code":"C-CYB 302","title":"Biometrics Security","unit":2,"status":"C","lh":15,"ph":45,"semester":"2","group":"B.Sc. Cybersecurity 300"},
    {"code":"C-CYB 303","title":"Cybersecurity Risks Analysis, Challenges and Mitigation","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. Cybersecurity 300"},
    {"code":"C-CYB 304","title":"Information and Big Data Security","unit":2,"status":"C","lh":15,"ph":45,"semester":"1","group":"B.Sc. Cybersecurity 400"},
    {"code":"C-CYB 401","title":"Systems Vulnerability Assessment and Testing","unit":2,"status":"C","lh":15,"ph":45,"semester":"1","group":"B.Sc. Cybersecurity 400"},
    {"code":"C-CYB 404","title":"Cloud Computing Security","unit":2,"status":"C","lh":30,"ph":0,"semester":"1","group":"B.Sc. Cybersecurity 500"},
    {"code":"C-ICT 305","title":"Data Communication System & Network","unit":3,"status":"C","lh":15,"ph":45,"semester":"1","group":"B.Sc. ICT 300"},
    {"code":"C-ICT 418","title":"Design and Installation of Electrical and ICT Services","unit":3,"status":"C","lh":30,"ph":45,"semester":"1","group":"B.Sc. ICT 400"},
    {"code":"C-UI-ICT 506","title":"Sensor Networks and Intelligent Systems","unit":2,"status":"E","lh":15,"ph":45,"semester":"2","group":"B.Sc. ICT 500"},
)
