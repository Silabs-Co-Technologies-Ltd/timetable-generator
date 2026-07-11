"""Local development entry point for IDEs such as PyCharm.

Run this file directly to start the Flask development server. Configuration is
loaded by ``create_app`` from environment variables and an optional local
``.env`` file in the project root.
"""

from __future__ import annotations

import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1").lower() in {"1", "true", "yes", "on"},
    )
