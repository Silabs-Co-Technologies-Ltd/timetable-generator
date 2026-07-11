from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.models import Course, Room, Timeslot


@dataclass(frozen=True)
class Assignment:
    course: Course
    room: Room
    timeslot: Timeslot


@dataclass(frozen=True)
class ScheduleResult:
    success: bool
    assignments: tuple[Assignment, ...]
    messages: tuple[str, ...]


def generate_schedule(
    courses: Iterable[Course], rooms: Iterable[Room], timeslots: Iterable[Timeslot]
) -> ScheduleResult:
    course_units = [
        course for course in courses for _ in range(max(course.weekly_contact_hours, 1))
    ]
    rooms = tuple(sorted(rooms, key=lambda room: room.capacity))
    timeslots = tuple(timeslots)

    if not course_units:
        return ScheduleResult(
            False, (), ("Add at least one course before generating a timetable.",)
        )
    if not rooms:
        return ScheduleResult(False, (), ("Add at least one room before generating a timetable.",))
    if not timeslots:
        return ScheduleResult(
            False, (), ("Add at least one teaching timeslot before generating a timetable.",)
        )

    assignments: list[Assignment] = []
    used_room_slots: set[tuple[int, int]] = set()
    used_lecturer_slots: set[tuple[int, int]] = set()
    used_group_slots: set[tuple[int, int]] = set()

    for course in sorted(course_units, key=lambda item: item.expected_class_size, reverse=True):
        placed = False
        for timeslot in timeslots:
            for room in rooms:
                if room.capacity < course.expected_class_size:
                    continue
                if course.requires_projection and not room.has_projection:
                    continue
                room_key = (room.id, timeslot.id)
                lecturer_key = (course.lecturer_id, timeslot.id)
                group_key = (course.student_group_id, timeslot.id)
                if (
                    room_key in used_room_slots
                    or lecturer_key in used_lecturer_slots
                    or group_key in used_group_slots
                ):
                    continue
                assignments.append(Assignment(course=course, room=room, timeslot=timeslot))
                used_room_slots.add(room_key)
                used_lecturer_slots.add(lecturer_key)
                used_group_slots.add(group_key)
                placed = True
                break
            if placed:
                break
        if not placed:
            return ScheduleResult(
                False,
                tuple(assignments),
                (f"Could not place {course.code}; add rooms, capacity, or free timeslots.",),
            )

    return ScheduleResult(True, tuple(assignments), ("Timetable generated successfully.",))
