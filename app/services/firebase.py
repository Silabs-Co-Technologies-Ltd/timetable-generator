from __future__ import annotations

import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check_firebase_connection() -> tuple[bool, str]:
    """Try a read-only Firebase Realtime Database connection when configured.

    Supabase remains the source of truth for timetable history; this helper only
    reports whether optional Firebase connectivity has enough environment
    configuration to be tested.
    """
    database_url = os.getenv("FIREBASE_DATABASE_URL", "").rstrip("/")
    if not database_url:
        return False, "Firebase is not configured. Set FIREBASE_DATABASE_URL to test it."

    token = os.getenv("FIREBASE_DATABASE_SECRET") or os.getenv("FIREBASE_AUTH_TOKEN")
    url = f"{database_url}/.json"
    if token:
        url = f"{url}?auth={token}"
    request = Request(url, method="GET")
    try:
        with urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                return True, "Firebase connection verified."
            return False, f"Firebase returned HTTP {response.status}."
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return False, f"Firebase connection failed with HTTP {exc.code}: {detail}"
    except URLError as exc:
        return False, f"Firebase connection failed: {exc.reason}"
