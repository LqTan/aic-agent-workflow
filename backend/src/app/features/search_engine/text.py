from __future__ import annotations

import re
import unicodedata

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def normalize_text(value: str) -> str:
    """Lowercase text and remove Vietnamese accents for deterministic matching."""
    value = unicodedata.normalize("NFD", value.casefold().replace("đ", "d"))
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return " ".join(TOKEN_PATTERN.findall(value))


def tokenize(value: str) -> set[str]:
    return set(normalize_text(value).split())
