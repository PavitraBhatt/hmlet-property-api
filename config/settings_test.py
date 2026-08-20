"""Settings used by the test suite.

Defaults to an in-memory SQLite database so `pytest` works on a fresh clone
with nothing installed locally. Set DB_ENGINE=postgres to run the same suite
against Postgres.
"""

import os

from .settings import *  # noqa: F401,F403

if os.getenv("DB_ENGINE") != "postgres":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

# Tests do not need a slow KDF.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
