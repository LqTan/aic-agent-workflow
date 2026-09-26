from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import asdict

from app.features.search_engine.lang import VI_TO_EN, normalize_ascii
from app.features.video_search.domain.models import (
    AgentTraceStep,
    SearchAttempt,
    SearchPlan,
    VideoSearchResponse,
)

logger = logging.getLogger(__name__)


OBJECT_TERMS = (
    "person", "man", "woman", "child", "bicycle", "motorcycle", "car",
    "bus", "dog", "cat", "traffic light", "boat", "phone", "bag",
)
ACTION_TERMS = ("riding", "walking", "running", "driving", "talking", "sitting")
SCENE_TERMS = ("street", "indoor", "outdoor", "beach", "airport", "market", "office")


def local_plan(query: str, collection_ids: list[str]) -> SearchPlan:
    normalized = normalize_ascii(query)
    expanded = normalized
    for source, targets in sorted(VI_TO_EN.items(), key=lambda item: -len(item[0])):
        for target in targets:
            expanded = _sub_word(expanded, source, target)

    objects = _find_terms(expanded, OBJECT_TERMS)
    actions = _find_terms(expanded, ACTION_TERMS)
    scenes = _find_terms(expanded, SCENE_TERMS)
    concepts = _unique([*objects, *actions, *scenes])
    search_query = query.strip()
    if concepts:
        search_query = f"{query.strip()}. Visual concepts: {', '.join(concepts)}."

    return SearchPlan(
        intent="video_retrieval",
        original_query=query.strip(),
        search_query=search_query,
        objects=tuple(objects),
        actions=tuple(actions),
        scenes=tuple(scenes),
        collection_ids=tuple(collection_ids),
        planner="local-deterministic",
    )


def evaluate_results(results: list[dict], plan: SearchPlan) -> float:
    if not results:
        return 0.0
    top = results[: min(5, len(results))]
    scores = [max(0.0, min(1.0, float(item.get("score", 0.0)))) for item in top]
    weighted = sum(score / (index + 1) for index, score in enumerate(scores))
    normalizer = sum(1 / (index + 1) for index in range(len(scores)))
    relevance = weighted / normalizer

    expected_objects = set(plan.objects)
    if not expected_objects:
        return round(relevance, 4)
    observed = {
        str(term).lower()
        for item in top
        for term in item.get("matched_objects", [])
    }
    coverage = len(expected_objects & observed) / len(expected_objects)
    return round(0.8 * relevance + 0.2 * coverage, 4)


def refine_query(plan: SearchPlan, attempt_number: int) -> str:
    concepts = _unique([*plan.objects, *plan.actions, *plan.scenes])
    if concepts:
        return "video keyframe showing " + ", ".join(concepts)
    return f"visual scene: {plan.original_query}"


def run_agent(
    *,
    query: str,
    collection_ids: list[str],
    top_k: int,
    quality_threshold: float,
    max_attempts: int,
    search_tool: Callable[..., tuple[dict, list[dict]]],
    planner: Callable[[str, list[str]], SearchPlan],
) -> dict:
    """Run the planner → search → evaluate → rewrite/retry loop."""
    plan = planner(query, collection_ids)
    trace: list[AgentTraceStep] = [
        AgentTraceStep(step="plan", status="completed", detail=asdict(plan))
    ]
    attempts: list[SearchAttempt] = []
    best_results: list[dict] = []
    best_parsed: dict = {"keys": [], "effective_collection_ids": collection_ids}
    best_quality = -1.0
    current_query = plan.search_query

    for attempt_number in range(1, max_attempts + 1):
        parsed, results = search_tool(
            query=current_query,
            collection_ids=collection_ids,
            top_k=top_k,
        )
        quality = evaluate_results(results, plan)
        accepted = bool(results) and quality >= quality_threshold
        attempt = SearchAttempt(
            attempt=attempt_number,
            query=current_query,
            result_count=len(results),
            quality_score=quality,
            threshold=quality_threshold,
            accepted=accepted,
        )
        attempts.append(attempt)
        trace.append(AgentTraceStep(step="search", status="completed", detail=asdict(attempt)))

        if quality > best_quality:
            best_quality = quality
            best_results = results
            best_parsed = parsed
        if accepted:
            trace.append(
                AgentTraceStep(
                    step="decide",
                    status="completed",
                    detail={"action": "return", "reason": "quality_threshold_met"},
                )
            )
            break
        if attempt_number < max_attempts:
            rewritten = refine_query(plan, attempt_number)
            trace.append(
                AgentTraceStep(
                    step="decide",
                    status="completed",
                    detail={
                        "action": "rewrite_and_retry",
                        "reason": "quality_below_threshold",
                        "next_query": rewritten,
                    },
                )
            )
            current_query = rewritten

    response = VideoSearchResponse(
        goal=query,
        plan=plan,
        attempts=attempts,
        trace=trace,
        decision="accepted" if best_quality >= quality_threshold else "best_effort",
        quality_score=max(best_quality, 0.0),
        count=len(best_results),
        results=[],
        filters_collection_ids=best_parsed.get("effective_collection_ids", collection_ids),
    )
    return {
        "response": response,
        "raw_results": best_results,
        "parsed": best_parsed,
    }


def _sub_word(text: str, source: str, target: str) -> str:
    import re

    return re.sub(rf"\b{re.escape(source)}\b", target, text)


def _find_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    import re

    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", text)]


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        cleaned = str(value).strip().lower()
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result


def clean_string_list(value, fallback) -> list[str]:
    """Public helper for planners to clean an LLM-provided list."""
    if not isinstance(value, list):
        return list(fallback)
    return _unique(item for item in value if isinstance(item, str))
