# Timetable Generator

A Python-based timetable generation project intended to run on Vercel. The application will help academic teams define scheduling inputs, generate conflict-aware timetables, review conflicts, manually adjust entries, and export finalized schedules.

## Current Status

Planning and requirements phase. The initial Software Requirements Document is available at [`docs/software-requirements.md`](docs/software-requirements.md).

> Note: The requested source DOCX document was not present in this repository when the requirements document was created. Add the DOCX to the repository and reconcile the SRD before implementation if it contains additional product requirements.

## Product Scope

The planned system will support:

- Teacher, subject, room, student group, working day, and timeslot management.
- Constraint configuration for availability, capacities, blocked periods, and subject frequency.
- Automated timetable generation using Python scheduling logic.
- Conflict detection for teachers, rooms, student groups, unavailable resources, and unscheduled sessions.
- Manual timetable editing with validation feedback.
- CSV export and printable views suitable for PDF workflows.
- Deployment as a Python project on Vercel.

## Proposed Technical Direction

- **Language:** Python
- **Deployment:** Vercel Python runtime
- **Web framework:** FastAPI or another Vercel-compatible Python framework
- **Scheduling engine:** Python module with hard and soft constraint handling
- **Persistence:** Database abstraction to support local development and production deployment
- **Testing:** Unit tests for scheduling constraints and integration tests for API behavior

## Repository Structure

```text
.
├── docs/
│   └── software-requirements.md
└── README.md
```

## Getting Started

Implementation has not started yet. Recommended next steps:

1. Confirm or add the missing DOCX source requirements document.
2. Reconcile the Software Requirements Document with the DOCX.
3. Scaffold the Vercel-compatible Python application.
4. Add domain models, validation schemas, and scheduling tests.
5. Build the timetable generation and review workflows incrementally.

## Deployment Target

This project is intended for Vercel. The implementation should include the necessary Vercel configuration, Python runtime entry points, and environment variable documentation before the first deployable release.

## Documentation

- [Software Requirements Document](docs/software-requirements.md)
