"""Vercel serverless entry point for the Flask application."""

from __future__ import annotations

import os

# Vercel's function filesystem is read-only except for /tmp. Keep the default
# SQLite database there unless the deployment explicitly provides another path.
os.environ.setdefault("SQLITE_DATABASE_PATH", "/tmp/timetable.sqlite3")

from app import create_app

app = create_app()
