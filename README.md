# Automated Timetable Generator

A Python-based web application for generating academic timetables using a constraint-based scheduling algorithm. The project requirements have been updated from `docs/Turaki_Ch1-3_Formatted.docx`, which describes an Automated Timetable Generator for academic institutions such as the Department of Computer Science, Nigerian Army University Biu (NAUB).

## Current Status

Planning and requirements phase. The reconciled Software Requirements Document is available at [`docs/software-requirements.md`](docs/software-requirements.md).

The current requirements are based on the project proposal in `docs/Turaki_Ch1-3_Formatted.docx`, especially Chapter Three's requirements analysis, system requirements specification, system architecture, and testing strategy.

## Product Scope

The planned system will support:

- Course management, including course code, title, assigned lecturer, expected class size, and weekly contact hours.
- Lecturer management and lecturer availability recording.
- Room management, including room code, seating capacity, and projection-facility status.
- Working day and time-slot configuration.
- Automated timetable generation using a Constraint Satisfaction Problem (CSP) model.
- Backtracking search with Minimum Remaining Values (MRV) ordering and forward checking.
- Conflict and infeasibility detection for lecturers, rooms, classes/student groups, capacities, unavailable periods, and unscheduled sessions.
- Timetable display in a day-by-time-slot grid with filtered views where supported.
- CSV and PDF exports for departmental publication.
- Administrative access control before production deployment.

## Proposed Technical Direction

The source proposal identifies the following preferred implementation stack:

- **Language:** Python 3.10+
- **Web framework:** Flask 3.0+
- **Templates:** Jinja2
- **Scheduling engine:** Constraint-based Python module using `python-constraint` 1.4+ or a custom CSP implementation
- **Algorithm:** Backtracking search with MRV heuristic and forward checking
- **Database:** SQLite 3 for development; MySQL 8+ for production
- **Frontend:** HTML5, CSS3, JavaScript (ES6)
- **Exports:** ReportLab 4.0+ for PDF and Python's built-in `csv` module for CSV
- **Production server:** Gunicorn or Apache with `mod_wsgi`
- **Deployment environment:** Institutional shared hosting, cPanel-compatible hosting, LAN deployment, or another confirmed Python hosting target

> Earlier planning mentioned Vercel as a possible deployment target. The reconciled DOCX requirements emphasize Flask and institutional/shared-hosting deployment. If Vercel is retained later, serverless execution limits, PDF generation, persistence, and offline/LAN requirements must be reassessed.

## Key Requirements

- Generate a complete timetable for up to 40 courses within 30 seconds on standard desktop or comparable server hardware.
- Produce timetables with zero hard-constraint violations when a valid solution exists.
- Provide actionable messages when a clash-free timetable is impossible with the supplied inputs.
- Remain usable by non-technical departmental administrators without specialist training.
- Support operation without continuous internet connectivity when deployed locally or on institutional infrastructure.

## Repository Structure

```text
.
├── docs/
│   ├── Turaki_Ch1-3_Formatted.docx
│   └── software-requirements.md
└── README.md
```

## Getting Started

Implementation has not started yet. Recommended next steps:

1. Confirm the production deployment target: institutional cPanel/shared hosting, LAN server, or another Python hosting environment.
2. Scaffold the Flask application with a modular project layout.
3. Define database models for courses, lecturers, rooms, availability, time slots, timetables, and audit events.
4. Implement CRUD workflows and validation for all scheduling inputs.
5. Build and test the CSP scheduling engine independently.
6. Add timetable grid views, conflict/infeasibility reporting, and export workflows.
7. Add authentication and role-based access control.
8. Document deployment and operational setup for the selected environment.

## Documentation

- [Software Requirements Document](docs/software-requirements.md)
- Source proposal: `docs/Turaki_Ch1-3_Formatted.docx`
