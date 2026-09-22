from __future__ import annotations

import re

from app.core.errors import InvalidSearchRequest
from app.features.video_search.domain.models import ParsedQuery

COLLECTION_TAG_PATTERN = re.compile(r"#(L\d+)\b", re.IGNORECASE)


def parse_query(query: str, collection_ids: list[str]) -> ParsedQuery:
    """Extract collection tags (#L##) from the user query, normalize the rest."""
    collection_tags = [
        match.group(1).upper() for match in COLLECTION_TAG_PATTERN.finditer(query)
    ]

    clean_query = COLLECTION_TAG_PATTERN.sub(" ", query)
    clean_query = re.sub(r"#(?=\w)", "", clean_query)
    clean_query = " ".join(clean_query.split())
    keys = clean_query.split()

    if not clean_query:
        raise InvalidSearchRequest("Query cần ít nhất một từ khóa tìm kiếm.")

    effective = _merge_collection_ids(collection_ids, collection_tags)
    return ParsedQuery(
        clean_query=clean_query,
        keys=keys,
        collection_tags=collection_tags,
        effective_collection_ids=effective,
    )


def _merge_collection_ids(*sources: list[str]) -> list[str]:
    result: list[str] = []
    for source in sources:
        for value in source:
            normalized = value.strip().upper()
            if normalized and normalized not in result:
                result.append(normalized)
    return result
