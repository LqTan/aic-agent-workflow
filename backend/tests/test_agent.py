from app.features.video_search.application.services.agent import (
    evaluate_results,
    local_plan,
    run_agent,
)


def test_local_plan_extracts_vietnamese_concepts() -> None:
    plan = local_plan("Tìm cảnh một người đang đi xe đạp ngoài đường", ["L21"])
    assert plan.intent == "video_retrieval"
    assert "person" in plan.objects
    assert "bicycle" in plan.objects
    assert "riding" in plan.actions
    assert "street" in plan.scenes
    assert plan.collection_ids == ("L21",)


def test_evaluate_rewards_object_coverage() -> None:
    plan = local_plan("người đi xe đạp", [])
    covered = evaluate_results(
        [{"score": 0.6, "matched_objects": ["person", "bicycle"]}],
        plan,
    )
    uncovered = evaluate_results(
        [{"score": 0.6, "matched_objects": []}],
        plan,
    )
    assert covered > uncovered


def test_run_agent_retries_when_quality_below_threshold() -> None:
    calls: list[str] = []

    def fake_search_tool(*, query, collection_ids, top_k):
        calls.append(query)
        score = 0.15 if len(calls) == 1 else 0.9
        return (
            {"keys": query.split(), "effective_collection_ids": collection_ids},
            [{"score": score, "matched_objects": ["person", "bicycle"]}],
        )

    result = run_agent(
        query="người đi xe đạp",
        collection_ids=[],
        top_k=5,
        quality_threshold=0.6,
        max_attempts=2,
        search_tool=fake_search_tool,
        planner=local_plan,
    )
    assert len(calls) == 2
    assert result["response"].decision == "accepted"
    assert result["response"].attempts[0].accepted is False
    assert result["response"].attempts[1].accepted is True
