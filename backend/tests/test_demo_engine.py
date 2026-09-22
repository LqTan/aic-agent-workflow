from app.features.search_engine.demo import inspect as demo_inspect
from app.features.search_engine.demo import search as demo_search


def test_demo_search_returns_ranked_results() -> None:
    results = demo_search(query="person bicycle riding", collection_ids=[], top_k=3)
    assert 1 <= len(results) <= 3
    for entry in results:
        assert entry["rank"] >= 1
        assert 0.0 <= entry["score"] <= 1.0
        assert "keyframe_id" in entry
        assert "matched_objects" in entry


def test_demo_search_filters_collections() -> None:
    results = demo_search(query="person", collection_ids=["UNKNOWN"], top_k=10)
    # All demo entries are in DEMO collection; filtering by unknown collection yields empty.
    assert results == []


def test_demo_inspect_returns_trace() -> None:
    trace = demo_inspect(query="người đi xe đạp", collection_ids=[], top_k=5)
    assert trace["query"]
    assert "routing" in trace
    assert "candidate_trace" in trace
