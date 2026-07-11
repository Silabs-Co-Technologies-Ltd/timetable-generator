# Automated Timetable Generator

A Python-based web application for generating academic timetables using a constraint-based scheduling algorithm. The project requirements have been updated from `docs/Turaki_Ch1-3_Formatted.docx`, which describes an Automated Timetable Generator for academic institutions such as the Department of Computer Science, Nigerian Army University Biu (NAUB).

## Current Status

Initial Flask project scaffold is in place. The reconciled Software Requirements Document is available at [`docs/software-requirements.md`](docs/software-requirements.md).

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

## Authentication and roles

The application now requires users to sign in before accessing timetable pages. Three roles are available:

- **Admin:** manage users, scheduling data, and timetable generation.
- **Scheduler:** manage scheduling data and generate timetables.
- **Viewer:** view the dashboard and generated timetables only.

On first startup, the app creates an initial admin account when no users exist. Configure it with `INITIAL_ADMIN_NAME`, `INITIAL_ADMIN_EMAIL`, and `INITIAL_ADMIN_PASSWORD`; otherwise the local-development defaults are `System Administrator`, `admin@example.com`, and `change-me-now`. Change that password immediately outside local development.

## Proposed Technical Direction

The source proposal identifies the following preferred implementation stack:

- **Language:** Python 3.10+
- **Web framework:** Flask 3.0+
- **Templates:** Jinja2
- **Scheduling engine:** Constraint-based Python module using `python-constraint` 1.4+ or a custom CSP implementation
- **Algorithm:** Backtracking search with MRV heuristic and forward checking
- **Database:** SQLite 3 for development and production persistence
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
├── app/
│   ├── models/              # SQLAlchemy data models
│   ├── routes/              # Flask blueprints and request handlers
│   ├── services/            # Scheduling and export services
│   ├── static/              # CSS and JavaScript assets
│   └── templates/           # Jinja2 templates
├── docs/                    # Requirements and source proposal
├── instance/                # Local SQLite database location (ignored)
├── tests/                   # Pytest suite
├── pyproject.toml           # Python package and tooling configuration
├── wsgi.py                  # Production WSGI entry point
└── README.md
```

## Getting Started

### Run locally from a terminal

1. Create and activate a virtual environment with Python 3.10 or newer.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and change the development secret and initial admin password if needed.
4. Start the development server:

   ```bash
   python run.py
   ```

5. Open <http://127.0.0.1:5000> and sign in with the configured initial admin account.

### Run in PyCharm

1. Open this repository folder as a PyCharm project.
2. Configure a Python 3.10+ virtual environment for the project interpreter.
3. Install packages from `requirements.txt` through PyCharm or with `python -m pip install -r requirements.txt` in the PyCharm terminal.
4. Copy `.env.example` to `.env` for local settings.
5. Create a **Python** run configuration with `run.py` as the script path, or right-click `run.py` and choose **Run**.

The app stores local SQLite data in `instance/timetable.sqlite3` by default. Delete that file if you want to reset local development data.

## Documentation

- [Software Requirements Document](docs/software-requirements.md)
- Source proposal: `docs/Turaki_Ch1-3_Formatted.docx`

## SQLite persistence and PDF export

The application uses SQLite 3 as its only database. All system data is stored through SQLAlchemy in the persistent SQLite file, including users, lecturers, student groups, rooms, timeslots, courses, generated timetables, timetable entries, and conflict summaries.

By default, the database file is created at `instance/timetable.sqlite3`. To store it elsewhere, set `SQLITE_DATABASE_PATH` to either an absolute path or a path relative to the Flask instance directory before starting the application. Keep the `instance/` directory or configured database path on persistent storage in production deployments so data survives restarts and redeploys.

Users can download any stored timetable as a PDF from the timetable detail page or from the latest-timetable link on the dashboard.
