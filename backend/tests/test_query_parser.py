import pytest

from app.core.errors import InvalidSearchRequest
from app.features.video_search.application.services.query_parser import parse_query


def test_extracts_collection_tag_and_keys() -> None:
    parsed = parse_query("Tìm cảnh đi xe đạp #L21 #l22", [])
    assert parsed.collection_tags == ["L21", "L22"]
    assert parsed.effective_collection_ids == ["L21", "L22"]
    assert "xe" in parsed.keys
    assert "đạp" in parsed.keys


def test_merges_explicit_collection_ids() -> None:
    parsed = parse_query("hello #L21", ["L99"])
    assert parsed.effective_collection_ids == ["L99", "L21"]


def test_rejects_empty_query() -> None:
    with pytest.raises(InvalidSearchRequest):
        parse_query("   ", [])
