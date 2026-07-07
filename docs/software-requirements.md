# Software Requirements Document: Automated Timetable Generator

## 1. Purpose

This document defines the software requirements for an **Automated Timetable Generator using a constraint-based algorithm for academic institutions**. It has been reconciled with `docs/Turaki_Ch1-3_Formatted.docx`, especially the Chapter Three requirements analysis, system requirements specification, architecture, and testing strategy.

The system is intended to replace manual departmental timetabling with a web-based application that lets non-technical academic administrators enter scheduling data, generate clash-free weekly timetables, review validation feedback, and export finalized schedules.

## 2. Project Overview

The proposed system supports departmental academic scheduling for environments such as the Department of Computer Science, Nigerian Army University Biu (NAUB). It will automate a process that is currently handled manually by a timetable officer using course lists, room registers, lecturer availability information, and previous semester timetables.

The core scheduling engine will model timetabling as a **Constraint Satisfaction Problem (CSP)**. Each course session is treated as a variable, and each possible `(day, time slot, room)` assignment is a domain value. The generator will use backtracking search, the Minimum Remaining Values (MRV) heuristic, and forward checking to produce schedules that satisfy required hard constraints while attempting to honor soft preferences.

## 3. Goals and Objectives

- Reduce the time and effort required to prepare departmental timetables.
- Generate weekly timetables with no hard scheduling clashes when a valid solution exists.
- Provide self-explanatory data-entry and validation workflows for non-technical administrators.
- Manage courses, lecturers, lecturer availability, rooms, and timetable outputs in one integrated web application.
- Detect impossible or inconsistent input data before or during generation and return actionable feedback.
- Export generated timetables as printable PDF and CSV files.
- Support deployment on institutional infrastructure, including shared hosting or local departmental environments.

## 4. Target Users and Roles

| Role | Description | Core Needs |
| --- | --- | --- |
| Administrator / Timetable Officer | Primary user responsible for entering data, generating timetables, and publishing outputs. | CRUD workflows, validation, generation, review, and export. |
| Lecturer | Academic staff member assigned to courses and availability periods. | Provide or review availability and view assigned teaching timetable. |
| Head of Department / Reviewer | Reviews generated timetables before publication. | View, verify, print, and approve schedules. |
| Student / Class Representative | Consumes published class timetable. | View class timetable in a readable format. |

## 5. Scope

### 5.1 In Scope

- Course management, including course code, title/name, assigned lecturer, expected class size, and weekly contact hours.
- Lecturer management and lecturer availability recording.
- Room management, including room code, seating capacity, and projection-facility availability.
- Weekly working-day and time-slot configuration.
- Automated timetable generation using a constraint-based backtracking algorithm with MRV and forward checking.
- Conflict detection for lecturers, rooms, student groups/classes, unavailable periods, room capacities, and unscheduled sessions.
- Validation and error reporting for input combinations that make a clash-free timetable impossible.
- Timetable display in a day-by-time-slot grid.
- Export to PDF and CSV.
- Role-protected administrative workflows.
- Testing and evaluation against measurable clash-free, performance, usability, and error-rate targets.

### 5.2 Out of Scope for Initial Build

- Native mobile applications.
- Attendance, grading, payroll, learning-management, or transcript features.
- Real-time collaborative editing.
- Full multi-department scheduling coordination, except as a future extension.
- Deep third-party Student Information System integration unless added later.

## 6. Functional Requirements

### FR-001: Course Management

The system shall allow an administrator to create, update, list, and delete course records containing course code, course name/title, assigned lecturer, expected class size, and number of weekly contact hours.

### FR-002: Lecturer and Availability Management

The system shall allow an administrator to create, update, list, and delete lecturer records and record the time periods during which each lecturer is available or unavailable to teach.

### FR-003: Room Management

The system shall maintain a register of available rooms, each with a unique room code, seating capacity, and projection-facility status.

### FR-004: Time Structure Configuration

The system shall allow configuration of working days and teaching time slots used by the timetable generator.

### FR-005: Timetable Generation

The system shall accept course, lecturer, room, availability, and time-slot inputs and generate a clash-free weekly timetable using a constraint satisfaction algorithm when a feasible solution exists.

### FR-006: Constraint Validation and Conflict Detection

The system shall detect and report hard-constraint violations, including lecturer double-booking, room double-booking, student group or class double-booking, unavailable lecturer assignments, unavailable room assignments, insufficient room capacity, and unscheduled required sessions.

### FR-007: Impossible Input Detection

The system shall detect and flag input data that makes a clash-free timetable impossible, such as insufficient room capacity, too few available time slots, or lecturer availability that cannot cover assigned weekly contact hours.

### FR-008: Timetable Views

The system shall display generated timetables in a grid format showing days of the week against time slots. It should also support filtered views by lecturer, room, and class/student group where the underlying data supports those views.

### FR-009: Export

The system shall export finalized timetable data to CSV and printable PDF.

### FR-010: Manual Review and Adjustment

The system should allow authorized users to review and adjust timetable entries after generation while preserving validation feedback for affected constraints.

### FR-011: Authentication and Authorization

The system should protect administrative data-entry, generation, and export workflows with role-based access control.

### FR-012: Auditability

The system should track timetable generation, edits, exports, and finalization events, including timestamps and actor identity where authentication is enabled.

## 7. Non-Functional Requirements

### 7.1 Usability

- The interface must be usable by a non-technical departmental administrator without specialist training.
- Forms, generation workflows, and validation messages must be self-explanatory.
- Error messages must identify the affected course, lecturer, room, class/student group, and time slot where applicable.

### 7.2 Performance

- The system must generate a complete timetable for a department of up to 40 courses within 30 seconds on standard desktop or comparable server hardware.
- Page interactions for CRUD, filtering, and viewing workflows should remain responsive.

### 7.3 Reliability

- The system must validate inputs before generation.
- The generator must fail safely with actionable feedback when constraints cannot be satisfied.
- Generated timetables must contain zero hard-constraint violations when a valid solution exists.

### 7.4 Offline and Network Operation

- The timetable generation workflow must be able to operate without continuous internet connectivity when deployed on local or institutional infrastructure.
- Multi-user access may use a local area network or institutional web hosting.

### 7.5 Security

- Administrative endpoints must be protected with authentication and authorization.
- User input must be validated and sanitized.
- Secrets and deployment credentials must not be committed to source control.

### 7.6 Maintainability

- The application should use modular Python code with clear separation between presentation, request handling, validation, persistence, scheduling logic, and exports.
- The scheduling engine should be independently testable.
- Automated tests should cover hard constraints, impossible-input detection, and export workflows.

### 7.7 Accessibility

- The user interface should use semantic HTML and accessible form controls.
- Timetable views should be readable with assistive technologies and navigable by keyboard.

## 8. Proposed Technical Architecture

The system follows a three-layer architecture:

| Layer | Responsibility |
| --- | --- |
| Presentation Layer | HTML5, CSS3, JavaScript, and server-rendered templates for forms, timetable grids, validation messages, and exports. |
| Logic Layer | Python web application, routing, validation, role-based access control, export routines, and the CSP scheduling engine. |
| Data Layer | Persistent storage for courses, lecturers, rooms, availability, generated timetables, and audit records. |

The preferred implementation stack from the source proposal is:

| Component | Technology / Version | Purpose |
| --- | --- | --- |
| Programming Language | Python 3.10+ | Core scheduling algorithm and backend application. |
| Web Framework | Flask 3.0+ | HTTP routing, request handling, and template rendering. |
| Constraint Library | `python-constraint` 1.4+ or custom implementation | CSP variable and constraint modelling. |
| Database | SQLite 3 for development; MySQL 8+ for production | Persistent storage. |
| Frontend | HTML5, CSS3, JavaScript (ES6) | Browser-based user interface. |
| Template Engine | Jinja2 | Dynamic HTML rendering. |
| Export Libraries | ReportLab 4.0+ and Python `csv` module | PDF and CSV export. |
| Web Server | Gunicorn or Apache with `mod_wsgi` | Production deployment. |
| Operating System | Linux, preferably Ubuntu 22.04 LTS, or Windows Server | Server environment. |
| Client Browser | Chrome 90+, Firefox 88+, Edge 90+, or Safari 14+ | Web interface access. |

Deployment should support shared institutional hosting such as cPanel-based infrastructure where possible. If a serverless target such as Vercel is retained in future, generation time limits and filesystem/database constraints must be reassessed.

## 9. Hardware Requirements

| Component | Minimum Specification | Recommended Specification |
| --- | --- | --- |
| Server Processor | Dual-core 2.0 GHz | Quad-core 2.5 GHz or higher |
| Server RAM | 1 GB | 2 GB or more |
| Server Storage | 5 GB free disk space | 20 GB free disk space |
| Client Device | Modern browser-capable device | Desktop/laptop with at least 1024 × 768 display |
| Network | LAN access for shared deployment | Stable LAN or internet connection for multi-user access |
| Power | Standard mains supply | UPS-backed mains supply |

## 10. Data Entities

| Entity | Example Attributes |
| --- | --- |
| Course | id, code, name, lecturer_id, expected_class_size, weekly_contact_hours |
| Lecturer | id, name, email, availability, unavailable_periods |
| Room | id, code, capacity, has_projection, availability |
| StudentGroup / Class | id, name, size, level, courses |
| Timeslot | id, day, start_time, end_time, label |
| CourseSession | id, course_id, duration/contact_hour_unit, required_count |
| Timetable | id, term, status, generated_at, generated_by, score, conflict_summary |
| TimetableEntry | id, timetable_id, course_id, lecturer_id, room_id, student_group_id, timeslot_id, locked |
| Constraint | id, type, severity, target_entity, value |
| AuditEvent | id, actor_id, action, target_type, target_id, created_at |

## 11. Scheduling Rules

### 11.1 Hard Constraints

- A lecturer cannot teach more than one course session in the same time slot.
- A room cannot host more than one course session in the same time slot.
- A student group or class cannot attend more than one course session in the same time slot.
- A course session cannot be assigned to a time when its lecturer is unavailable.
- A course session cannot be assigned to a room that is unavailable.
- Room capacity must be sufficient for the expected class size.
- All required weekly contact hours must be scheduled unless the system reports an infeasible input set.

### 11.2 Soft Constraints

- Honor lecturer preferred time slots where possible.
- Distribute sessions reasonably across the week.
- Avoid excessive consecutive periods for a lecturer.
- Prefer rooms with projection facilities for courses that need them.
- Minimize idle gaps for lecturers and student groups where possible.

## 12. Algorithm Requirements

- The scheduling problem shall be represented as a CSP.
- Each course session shall be a CSP variable.
- Each domain value shall represent an eligible `(day, time slot, room)` assignment.
- The generator shall use backtracking search.
- The generator should use the Minimum Remaining Values heuristic to select the next variable.
- The generator should use forward checking to prune conflicting domain values after each assignment.
- The generator shall backtrack when an unassigned variable has an empty domain.
- The generator shall return either a valid timetable or a structured explanation of why no valid timetable was found.

## 13. User Experience Requirements

- Users should follow a logical workflow: rooms, lecturers, lecturer availability, courses, time slots, generation, review, export.
- Generation results should clearly state whether the timetable is complete, incomplete, or infeasible.
- Validation messages should be contextual and actionable.
- Timetable grids should be clear enough for printing and departmental publication.

## 14. Testing and Evaluation Requirements

The system shall be evaluated using clash-detection testing, functional validation testing, and user acceptance testing.

| Metric | Definition | Target Value |
| --- | --- | --- |
| Clash-Free Rate | Percentage of generated timetables with zero hard-constraint violations. | 100% |
| Timetable Generation Time | Elapsed time for a representative 30-course instance. | ≤ 30 seconds |
| Time Reduction vs. Manual | Improvement over the documented manual process duration. | ≥ 10× |
| Soft Constraint Satisfaction Rate | Percentage of lecturer preferences honored. | ≥ 70% |
| System Usability Score | Mean user acceptance rating on a 5-point scale. | ≥ 4.0 / 5.0 |
| Interface Error Rate | Percentage of interactions that produce unhandled exceptions or misleading errors. | 0% |

## 15. Acceptance Criteria

- Administrators can create, update, list, and delete course, lecturer, room, availability, and time-slot data.
- Administrators can generate a timetable from representative departmental data.
- Generated timetables contain no hard-constraint violations when a valid solution exists.
- The system reports actionable infeasibility messages when valid generation is impossible.
- Users can view timetables in a day/time grid and filter views by lecturer, room, or class where applicable.
- Users can export timetable data to CSV and PDF.
- The system can generate a timetable for up to 40 courses within 30 seconds on the target hardware.
- Administrative workflows are protected by authentication or an equivalent access-control mechanism before production deployment.

## 16. Risks and Open Questions

- The exact production hosting target must be confirmed: institutional cPanel/shared hosting, LAN deployment, or a serverless provider.
- If Vercel remains a target, Python serverless limits may conflict with longer-running CSP generation and PDF export requirements.
- Authentication and database providers must be selected before implementation.
- Multi-department scheduling is a future extension and is not part of the initial scope.
- Representative NAUB scheduling datasets should be prepared for repeatable testing.

## 17. Initial Implementation Milestones

1. Scaffold the Python web application using Flask, Jinja2 templates, and a modular project layout.
2. Define database models and migrations for courses, lecturers, rooms, availability, time slots, timetables, and audit events.
3. Implement CRUD workflows and validation for core scheduling inputs.
4. Implement the CSP scheduling engine with hard-constraint validation, MRV ordering, and forward checking.
5. Add timetable grid views and filtered timetable views.
6. Add infeasibility and conflict-reporting workflows.
7. Add CSV and PDF export workflows.
8. Add authentication and role-based access control.
9. Add automated tests for scheduling rules, impossible-input detection, exports, and key web workflows.
10. Document deployment for the selected institutional hosting environment.
