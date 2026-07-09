from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.models import Timetable


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    key: str
    table: str = "timetable_history"

    @classmethod
    def from_env(cls) -> "SupabaseConfig | None":
        url = os.getenv("SUPABASE_URL", "").rstrip("/")
        key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
        table = os.getenv("SUPABASE_TIMETABLE_TABLE", "timetable_history")
        if not url or not key:
            return None
        return cls(url=url, key=key, table=table)


def timetable_payload(timetable: Timetable) -> dict[str, Any]:
    return {
        "local_id": timetable.id,
        "term": timetable.term,
        "status": timetable.status,
        "generated_at": timetable.generated_at.isoformat(),
        "conflict_summary": timetable.conflict_summary or "",
        "entries": [
            {
                "course_code": entry.course.code,
                "course_title": entry.course.title,
                "lecturer": entry.lecturer.name,
                "room": entry.room.code,
                "student_group": entry.student_group.name,
                "day": entry.timeslot.day,
                "time": entry.timeslot.label,
            }
            for entry in timetable.entries
        ],
    }


def sync_timetable_history(timetable: Timetable, config: SupabaseConfig | None = None) -> tuple[bool, str]:
    """Persist generated timetable history to Supabase PostgREST when configured."""
    config = config or SupabaseConfig.from_env()
    if config is None:
        return False, "Supabase is not configured."

    endpoint = f"{config.url}/rest/v1/{config.table}"
    payload = json.dumps(timetable_payload(timetable)).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "apikey": config.key,
            "Authorization": f"Bearer {config.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                return True, "Timetable history synced to Supabase."
            return False, f"Supabase returned HTTP {response.status}."
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return False, f"Supabase sync failed with HTTP {exc.code}: {detail}"
    except URLError as exc:
        return False, f"Supabase sync failed: {exc.reason}"
