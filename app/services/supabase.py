from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models import Timetable


SUPABASE_URL_ENV_NAMES = ("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY_ENV_NAMES = (
    "SUPABASE_SECRET_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_KEY",
    "SUPABASE_ANON_KEY",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
)


def _first_env_value(names: tuple[str, ...]) -> str:
    return next((value for name in names if (value := os.getenv(name, "").strip())), "")


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    key: str
    table: str = "timetable_history"

    @classmethod
    def from_env(cls) -> "SupabaseConfig | None":
        url = _first_env_value(SUPABASE_URL_ENV_NAMES).rstrip("/")
        key = _first_env_value(SUPABASE_KEY_ENV_NAMES)
        table = os.getenv("SUPABASE_TIMETABLE_TABLE", "timetable_history")
        if not url or not key:
            return None
        return cls(url=url, key=key, table=table)

    @classmethod
    def missing_env_names(cls) -> list[str]:
        missing = []
        if not _first_env_value(SUPABASE_URL_ENV_NAMES):
            missing.append(" or ".join(SUPABASE_URL_ENV_NAMES))
        if not _first_env_value(SUPABASE_KEY_ENV_NAMES):
            missing.append(", ".join(SUPABASE_KEY_ENV_NAMES[:-1]) + f", or {SUPABASE_KEY_ENV_NAMES[-1]}")
        return missing

    @property
    def endpoint(self) -> str:
        return f"{self.url}/rest/v1/{self.table}"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }


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


def _read_json(request: Request, timeout: int = 10) -> Any:
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        if not body:
            return None
        return json.loads(body)


def _error_message(prefix: str, exc: HTTPError | URLError) -> str:
    if isinstance(exc, HTTPError):
        detail = exc.read().decode("utf-8", errors="replace")
        return f"{prefix} failed with HTTP {exc.code}: {detail}"
    return f"{prefix} failed: {exc.reason}"


def _missing_config_message() -> str:
    missing = SupabaseConfig.missing_env_names()
    if not missing:
        return "Supabase is not configured."
    return f"Supabase is not configured. Missing: {', '.join(missing)}."


def check_supabase_connection(config: SupabaseConfig | None = None) -> tuple[bool, str]:
    """Validate that Supabase credentials can read the timetable history table."""
    config = config or SupabaseConfig.from_env()
    if config is None:
        return False, _missing_config_message()

    query = urlencode({"select": "id", "limit": "1"})
    request = Request(f"{config.endpoint}?{query}", headers=config.headers, method="GET")
    try:
        _read_json(request)
        return True, "Supabase connection verified."
    except (HTTPError, URLError) as exc:
        return False, _error_message("Supabase connection", exc)


def fetch_timetable_history(limit: int = 10, config: SupabaseConfig | None = None) -> tuple[list[dict[str, Any]], str]:
    """Fetch recent timetable history rows from Supabase when configured."""
    config = config or SupabaseConfig.from_env()
    if config is None:
        return [], _missing_config_message()

    query = urlencode(
        {
            "select": "id,local_id,term,status,generated_at,conflict_summary,entries,inserted_at",
            "order": "generated_at.desc",
            "limit": str(limit),
        }
    )
    request = Request(f"{config.endpoint}?{query}", headers=config.headers, method="GET")
    try:
        rows = _read_json(request)
        return rows if isinstance(rows, list) else [], "Supabase history loaded."
    except (HTTPError, URLError) as exc:
        return [], _error_message("Supabase history load", exc)


def sync_timetable_history(timetable: Timetable, config: SupabaseConfig | None = None) -> tuple[bool, str]:
    """Persist generated timetable history to Supabase PostgREST when configured."""
    config = config or SupabaseConfig.from_env()
    if config is None:
        return False, _missing_config_message()

    payload = json.dumps(timetable_payload(timetable)).encode("utf-8")
    request = Request(
        config.endpoint,
        data=payload,
        method="POST",
        headers={**config.headers, "Prefer": "resolution=merge-duplicates,return=minimal"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                return True, "Timetable history synced to Supabase."
            return False, f"Supabase returned HTTP {response.status}."
    except (HTTPError, URLError) as exc:
        return False, _error_message("Supabase sync", exc)
