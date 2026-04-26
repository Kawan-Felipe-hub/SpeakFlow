from __future__ import annotations

import os


env = os.environ.get("APP_ENV", "dev").lower()
if env in {"prod", "production"}:
    from speakflow.settings.prod import *  # noqa: F403
else:
    from speakflow.settings.dev import *  # noqa: F403

