# Software Requirements Document: Timetable Generator

## 1. Purpose

This document defines the software requirements for a Python-based timetable generation application intended to be deployed on Vercel. It establishes the initial scope, user roles, functional requirements, non-functional requirements, data model expectations, integrations, and acceptance criteria needed before implementation begins.

> Note: No DOCX source document was present in the repository at the time this SRD was created. The requirements below are structured from the project name, the requested Vercel Python deployment target, and standard timetable-generation product needs. If the DOCX is added later, this SRD should be reconciled against it.

## 2. Project Overview

The Timetable Generator will help academic administrators create conflict-free class schedules from constraints such as courses, teachers, rooms, student groups, working days, timeslots, and institutional scheduling rules. The system should support generating a timetable, reviewing conflicts, manually adjusting entries, and exporting finalized schedules.

## 3. Goals and Objectives

- Provide a simple web interface for creating and managing timetable input data.
- Generate valid timetables that minimize conflicts across teachers, rooms, student groups, and timeslots.
- Support constraint-aware scheduling rules such as room capacity, teacher availability, subject periods per week, and blocked timeslots.
- Allow users to inspect, edit, regenerate, and export generated timetables.
- Run as a Python web application deployed on Vercel with a clear path for local development and production deployment.

## 4. Target Users and Roles

| Role | Description | Core Needs |
| --- | --- | --- |
| Administrator | Owns institutional setup and user access. | Configure academic structure and manage data. |
| Scheduler | Creates and validates timetables. | Generate, edit, resolve conflicts, and export schedules. |
| Teacher | Reviews assigned teaching timetable. | View personal schedule and availability impact. |
| Student or Class Representative | Reviews class timetable. | View class or group schedule. |

## 5. Scope

### 5.1 In Scope

- Course, teacher, room, student group, and timeslot management.
- Teacher availability and room availability constraints.
- Automated timetable generation using a Python scheduling algorithm.
- Conflict detection and validation summaries.
- Manual timetable adjustments after generation.
- Export to CSV and printable PDF-ready views.
- Deployment-ready configuration for Vercel Python runtimes.

### 5.2 Out of Scope for Initial Build

- Native mobile applications.
- Real-time multi-user collaborative editing.
- Payroll, attendance, grading, or learning-management features.
- Deep integration with third-party student information systems unless added later.

## 6. Functional Requirements

### FR-001: Academic Data Management

The system shall allow administrators and schedulers to create, update, list, and delete teachers, subjects, rooms, student groups, academic terms, working days, and timeslots.

### FR-002: Constraint Configuration

The system shall allow users to define required constraints, including teacher availability, room availability, subject frequency, room capacity, room type, and blocked periods.

### FR-003: Timetable Generation

The system shall generate a timetable using the configured academic data and constraints. The generator should attempt to produce a complete timetable with no hard-constraint violations.

### FR-004: Conflict Detection

The system shall detect and report conflicts, including teacher double-booking, room double-booking, student group double-booking, unavailable teacher assignments, unavailable room assignments, and unscheduled required sessions.

### FR-005: Manual Editing

The system shall allow authorized users to move, add, remove, and lock timetable entries after generation while preserving conflict validation feedback.

### FR-006: Regeneration with Locked Entries

The system shall allow users to lock selected timetable entries and regenerate remaining entries without moving locked items.

### FR-007: Timetable Views

The system shall provide timetable views by class or student group, teacher, room, day, and full institution schedule.

### FR-008: Export

The system shall export timetable data to CSV and provide printable browser views suitable for saving as PDF.

### FR-009: Authentication and Authorization

The system should support authenticated access for administrative and scheduling actions. Public or read-only timetable viewing may be configurable.

### FR-010: Auditability

The system should track when timetables are generated, edited, exported, and finalized, including the actor where authentication is enabled.

## 7. Non-Functional Requirements

### Performance

- Generate small to medium school timetables within an acceptable interactive response time.
- Provide asynchronous or queued generation if generation time exceeds typical request limits.
- Keep page interactions responsive for common CRUD and viewing workflows.

### Reliability

- Validate inputs before generation.
- Preserve existing timetable versions before regeneration.
- Fail safely with actionable error messages when constraints are impossible to satisfy.

### Security

- Protect administrative endpoints with authentication and authorization.
- Validate and sanitize user input.
- Avoid exposing secrets in source control or client-side code.

### Maintainability

- Use modular Python code with separate layers for routing, validation, persistence, generation logic, and presentation.
- Include automated tests for scheduling constraints and API behavior.
- Keep deployment configuration documented and reproducible.

### Accessibility

- Use semantic HTML and accessible form controls.
- Ensure timetable views are keyboard navigable and readable with assistive technologies.

## 8. Proposed Technical Architecture

- **Runtime:** Python on Vercel.
- **Web framework:** FastAPI or another Vercel-compatible Python web framework.
- **Frontend:** Server-rendered templates or a lightweight client interface, depending on implementation needs.
- **Scheduling engine:** Python service module implementing hard and soft constraints.
- **Persistence:** Start with a simple database abstraction suitable for local development and later production database integration.
- **Deployment:** Vercel project configured for Python serverless functions.

## 9. Data Entities

| Entity | Example Attributes |
| --- | --- |
| Teacher | id, name, email, availability, max_periods_per_day |
| Subject | id, name, required_periods_per_week, preferred_room_type |
| Room | id, name, capacity, room_type, availability |
| StudentGroup | id, name, size, curriculum_subjects |
| Timeslot | id, day, start_time, end_time, label |
| TimetableEntry | id, timetable_id, subject_id, teacher_id, room_id, student_group_id, timeslot_id, locked |
| Constraint | id, type, severity, target_entity, value |
| TimetableRun | id, status, created_by, created_at, score, conflict_summary |

## 10. Scheduling Rules

### Hard Constraints

- A teacher cannot teach more than one class in the same timeslot.
- A room cannot host more than one class in the same timeslot.
- A student group cannot attend more than one class in the same timeslot.
- A class cannot be scheduled when the assigned teacher or room is unavailable.
- Room capacity must be sufficient for the assigned student group.

### Soft Constraints

- Distribute subjects evenly across the week where possible.
- Avoid excessive consecutive teaching periods for a teacher.
- Prefer specialized rooms for subjects that require them.
- Minimize idle gaps for teachers and student groups.

## 11. User Experience Requirements

- Users should be guided through setup in a logical sequence: academic calendar, rooms, teachers, subjects, student groups, constraints, generation, review, export.
- Generation results should clearly show whether the timetable is complete, partially complete, or invalid.
- Conflict messages should identify the affected teacher, room, student group, subject, and timeslot.
- Manual edits should immediately re-run validation for affected entries.

## 12. Acceptance Criteria

- Users can define core academic data needed for timetable generation.
- Users can generate a timetable from sample data.
- Generated timetables do not violate hard constraints when a valid solution exists.
- Conflicts are displayed when a valid solution cannot be produced.
- Users can view timetables by teacher, room, and student group.
- Users can export timetable data to CSV and print timetable views.
- The application can be deployed to Vercel as a Python project.

## 13. Risks and Open Questions

- The source DOCX requirements need to be added or located and reconciled with this SRD.
- The expected institution size is unknown and may affect algorithm choice.
- Authentication provider and database provider are not yet selected.
- Vercel serverless execution limits may require asynchronous generation for larger timetables.
- Export format expectations should be confirmed before implementation.

## 14. Initial Implementation Milestones

1. Project scaffold for Python on Vercel.
2. Domain models and validation schemas.
3. CRUD workflows for academic data.
4. Initial scheduling engine with hard-constraint validation.
5. Timetable views and conflict summaries.
6. Manual edit and locked-entry regeneration support.
7. Export workflows.
8. Deployment, testing, and documentation hardening.
