from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
import os
import re
from typing import Callable
from urllib import error, request


logger = logging.getLogger(__name__)


VI_TO_EN = {
    "nguoi": "person",
    "dan ong": "man",
    "phu nu": "woman",
    "tre em": "child",
    "xe dap": "bicycle",
    "xe may": "motorcycle",
    "o to": "car",
    "xe buyt": "bus",
    "duong pho": "street",
    "ngoai duong": "street",
    "trong nha": "indoor",
    "ngoai troi": "outdoor",
    "ao do": "red shirt",
    "ao xanh": "blue shirt",
    "di bo": "walking",
    "dang di": "riding",
    "cho": "dog",
    "meo": "cat",
    "bien": "beach",
    "san bay": "airport",
}

OBJECT_TERMS = (
    "person", "man", "woman", "child", "bicycle", "motorcycle", "car",
    "bus", "dog", "cat", "traffic light", "boat", "phone", "bag",
)
ACTION_TERMS = ("riding", "walking", "running", "driving", "talking", "sitting")
SCENE_TERMS = ("street", "indoor", "outdoor", "beach", "airport", "market", "office")


@dataclass(frozen=True)
class AgentPlan:
    intent: str
    original_query: str
    search_query: str
    objects: tuple[str, ...]
    actions: tuple[str, ...]
    scenes: tuple[str, ...]
    collection_ids: tuple[str, ...]
    planner: str


def normalize_ascii(text: str) -> str:
    replacements = str.maketrans(
        "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd",
    )
    return " ".join(text.lower().translate(replacements).split())


def local_plan(query: str, collection_ids: list[str]) -> AgentPlan:
    normalized = normalize_ascii(query)
    expanded = normalized
    for source, target in sorted(VI_TO_EN.items(), key=lambda item: -len(item[0])):
        expanded = re.sub(rf"\b{re.escape(source)}\b", target, expanded)

    objects = _find_terms(expanded, OBJECT_TERMS)
    actions = _find_terms(expanded, ACTION_TERMS)
    scenes = _find_terms(expanded, SCENE_TERMS)
    concepts = _unique([*objects, *actions, *scenes])
    search_query = query.strip()
    if concepts:
        search_query = f"{query.strip()}. Visual concepts: {', '.join(concepts)}."

    return AgentPlan(
        intent="video_retrieval",
        original_query=query.strip(),
        search_query=search_query,
        objects=tuple(objects),
        actions=tuple(actions),
        scenes=tuple(scenes),
        collection_ids=tuple(collection_ids),
        planner="local-deterministic",
    )


def build_plan(query: str, collection_ids: list[str]) -> AgentPlan:
    """Use an OpenAI-compatible LLM when configured, otherwise stay offline."""
    api_key = os.getenv("KIS_LLM_API_KEY", "").strip()
    endpoint = os.getenv("KIS_LLM_ENDPOINT", "").strip()
    model = os.getenv("KIS_LLM_MODEL", "").strip()
    if not api_key or not endpoint or not model:
        return local_plan(query, collection_ids)

    fallback = local_plan(query, collection_ids)
    prompt = (
        "Analyze this Vietnamese/English video retrieval goal. Return JSON only "
        "with string arrays objects, actions, scenes and a concise English search_query. "
        f"Goal: {query}"
    )
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
    ).encode("utf-8")
    http_request = request.Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return AgentPlan(
            intent="video_retrieval",
            original_query=query.strip(),
            search_query=str(parsed.get("search_query") or fallback.search_query).strip(),
            objects=tuple(_clean_list(parsed.get("objects"), fallback.objects)),
            actions=tuple(_clean_list(parsed.get("actions"), fallback.actions)),
            scenes=tuple(_clean_list(parsed.get("scenes"), fallback.scenes)),
            collection_ids=tuple(collection_ids),
            planner=f"llm:{model}",
        )
    except (error.URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        logger.warning("LLM planner unavailable; using local planner: %s", exc)
        return fallback


def run_agent(
    *,
    query: str,
    collection_ids: list[str],
    top_k: int,
    quality_threshold: float,
    max_attempts: int,
    search_tool: Callable[..., tuple[dict, list[dict]]],
) -> dict:
    plan = build_plan(query, collection_ids)
    trace: list[dict] = [
        {
            "step": "plan",
            "status": "completed",
            "detail": asdict(plan),
        }
    ]
    attempts: list[dict] = []
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
        attempt = {
            "attempt": attempt_number,
            "query": current_query,
            "result_count": len(results),
            "quality_score": quality,
            "threshold": quality_threshold,
            "accepted": accepted,
        }
        attempts.append(attempt)
        trace.append({"step": "search", "status": "completed", "detail": attempt})

        if quality > best_quality:
            best_quality = quality
            best_results = results
            best_parsed = parsed
        if accepted:
            trace.append(
                {
                    "step": "decide",
                    "status": "completed",
                    "detail": {"action": "return", "reason": "quality_threshold_met"},
                }
            )
            break
        if attempt_number < max_attempts:
            rewritten = refine_query(plan, attempt_number)
            trace.append(
                {
                    "step": "decide",
                    "status": "completed",
                    "detail": {
                        "action": "rewrite_and_retry",
                        "reason": "quality_below_threshold",
                        "next_query": rewritten,
                    },
                }
            )
            current_query = rewritten

    return {
        "goal": query,
        "plan": asdict(plan),
        "attempts": attempts,
        "trace": trace,
        "decision": "accepted" if best_quality >= quality_threshold else "best_effort",
        "quality_score": max(best_quality, 0.0),
        "parsed_info": best_parsed,
        "results": best_results,
    }


def evaluate_results(results: list[dict], plan: AgentPlan) -> float:
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


def refine_query(plan: AgentPlan, attempt_number: int) -> str:
    concepts = _unique([*plan.objects, *plan.actions, *plan.scenes])
    if concepts:
        return "video keyframe showing " + ", ".join(concepts)
    return f"visual scene: {plan.original_query}"


def _find_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", text)]


def _unique(values) -> list[str]:
    result = []
    for value in values:
        cleaned = str(value).strip().lower()
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result


def _clean_list(value, fallback) -> list[str]:
    if not isinstance(value, list):
        return list(fallback)
    return _unique(item for item in value if isinstance(item, str))
