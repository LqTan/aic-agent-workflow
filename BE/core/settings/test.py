from .base import *  # noqa: F403,F401


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
KIS_SEARCH_FUNCTION = "search_engine.demo.search"
KIS_INSPECT_FUNCTION = "search_engine.demo.inspect"
