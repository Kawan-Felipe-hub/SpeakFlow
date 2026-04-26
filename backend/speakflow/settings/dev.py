from __future__ import annotations

from .base import *  # noqa: F403
from .upload_limits import *  # noqa: F403

DEBUG = True

# Dev default: SQLite to enable quick local testing without Postgres.
# Set USE_SQLITE=false (and configure DATABASE_URL/POSTGRES_*) to use Postgres locally.
if os.environ.get("USE_SQLITE", "true").lower() == "true":  # noqa: F405
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

