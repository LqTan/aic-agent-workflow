from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import Settings, get_settings
from app.core.errors import (
    InvalidSearchRequest,
    RunNotFound,
)
from app.features.search_run.infrastructure.repository import (
    SqlModelSearchRunRepository,
)
from app.features.video_search.application.services.agent import (
    evaluate_results,
    refine_query,
)
from app.features.video_search.dependency_injection import (
    build_agent_use_case,
    build_engine,
    build_planner,
)
from app.features.video_search.domain.models import (
    SearchPlan,
    VideoSearchRequest,
)
from app.features.video_search.presentation.url_builder import (
    format_results_with_urls,
)

router = APIRouter(prefix="/kis/tools", tags=["KIS Tools"])

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def _public_base_url(settings: Settings) -> str:
    """Base URL the tools use to build absolute asset URLs.

    Inside docker compose ``APP_PUBLIC_BASE_URL`` defaults to ``http://backend:8000``
    so n8n (which talks to backend by service name) gets URLs that resolve inside
    the docker network. Override per environment as needed.
    """
    return settings.app_public_base_url.rstrip("/")


@router.post("/planner", summary="Build a SearchPlan for a query (n8n tool)")
async def planner_tool(payload: dict) -> dict:
    query = (payload.get("query") or "").strip()
    if not query:
        raise InvalidSearchRequest("Query không được rỗng.")
    collection_ids = list(payload.get("collection_ids") or [])
    planner = build_planner(get_settings())
    plan = planner.plan(query, collection_ids)
    return {
        "planner": plan.planner,
        "plan": {
            "intent": plan.intent,
            "original_query": plan.original_query,
            "search_query": plan.search_query,
            "objects": list(plan.objects),
            "actions": list(plan.actions),
            "scenes": list(plan.scenes),
            "collection_ids": list(plan.collection_ids),
        },
    }


@router.post("/retrieval", summary="Retrieve and rerank keyframes (n8n tool)")
async def retrieval_tool(
    payload: dict,
    settings: Settings = Depends(get_settings),
) -> dict:
    query = (payload.get("query") or "").strip()
    if not query:
        raise InvalidSearchRequest("Query không được rỗng.")
    engine = build_engine(settings)
    collection_ids = list(payload.get("collection_ids") or [])
    top_k = int(payload.get("top_k") or 12)
    parsed, results = engine.search(
        query=query, collection_ids=collection_ids, top_k=top_k
    )
    enrich = bool(payload.get("enrich_urls", True))
    if enrich:
        results = format_results_with_urls(
            results=results, source=_public_base_url(settings)
        )
    return {
        "parsed": parsed,
        "results": results,
        "result_count": len(results),
    }


@router.post("/validation", summary="Score candidate results against a plan (n8n tool)")
async def validation_tool(payload: dict) -> dict:
    plan_payload = payload.get("plan") or {}
    plan = SearchPlan(
        intent=plan_payload.get("intent", "video_retrieval"),
        original_query=plan_payload.get("original_query", ""),
        search_query=plan_payload.get("search_query", ""),
        objects=tuple(plan_payload.get("objects", [])),
        actions=tuple(plan_payload.get("actions", [])),
        scenes=tuple(plan_payload.get("scenes", [])),
        collection_ids=tuple(plan_payload.get("collection_ids", [])),
        planner=plan_payload.get("planner", "local-deterministic"),
    )
    results = list(payload.get("results") or [])
    threshold = float(payload.get("threshold") or 0.42)
    quality = evaluate_results(results, plan)
    return {
        "quality_score": quality,
        "threshold": threshold,
        "accepted": bool(results) and quality >= threshold,
    }


@router.post("/rewrite", summary="Rewrite a query for the next retry (n8n tool)")
async def rewrite_tool(payload: dict) -> dict:
    plan_payload = payload.get("plan") or {}
    plan = SearchPlan(
        intent=plan_payload.get("intent", "video_retrieval"),
        original_query=plan_payload.get("original_query", ""),
        search_query=plan_payload.get("search_query", ""),
        objects=tuple(plan_payload.get("objects", [])),
        actions=tuple(plan_payload.get("actions", [])),
        scenes=tuple(plan_payload.get("scenes", [])),
        collection_ids=tuple(plan_payload.get("collection_ids", [])),
        planner=plan_payload.get("planner", "local-deterministic"),
    )
    attempt_number = int(payload.get("attempt") or 1)
    return {"next_query": refine_query(plan, attempt_number)}


@router.post(
    "/agent",
    summary="Full agent search in a single call (test/dev convenience).",
)
async def agent_tool(
    payload: dict,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Convenience entry point that runs the full planner → retrieve → evaluate
    → rewrite loop in one request. Useful for direct curl tests; the canonical
    workflow should orchestrate the per-step ``/kis/tools/*`` endpoints from
    n8n so the agent steps are observable there.
    """
    query = (payload.get("query") or "").strip()
    if not query:
        raise InvalidSearchRequest("Query không được rỗng.")
    request = VideoSearchRequest(
        query=query,
        collection_ids=list(payload.get("collection_ids") or []),
        top_k=int(payload.get("top_k") or 12),
        quality_threshold=float(payload.get("quality_threshold") or 0.42),
        max_attempts=int(payload.get("max_attempts") or 2),
    )
    use_case = build_agent_use_case(settings)
    response = await use_case.execute(request)
    response["results"] = format_results_with_urls(
        results=response["results"], source=_public_base_url(settings)
    )
    return response


@router.post(
    "/finalize/{run_id}",
    summary="Return the full saved run response with enriched asset URLs (n8n tool).",
)
async def finalize_run(
    run_id: str,
    settings: Settings = Depends(get_settings),
) -> dict:
    repository = SqlModelSearchRunRepository()
    record = await repository.get(run_id)
    if record is None:
        raise RunNotFound(f"Run {run_id} không tồn tại.")

    base_url = _public_base_url(settings)
    enriched_results = format_results_with_urls(
        results=list(record.results or []),
        source=base_url,
    )
    return {
        "id": record.id,
        "goal": record.goal,
        "query": record.query,
        "timestamp": record.timestamp.isoformat(),
        "quality_score": record.quality_score,
        "decision": record.decision,
        "result_count": record.result_count,
        "attempts": record.attempts,
        "duration_ms": record.duration_ms,
        "collection_ids": record.collection_ids,
        "planner": record.planner,
        "plan": record.plan,
        "trace": record.trace,
        "attempt_details": record.attempt_details,
        "results": enriched_results,
    }


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload one or more videos (multipart/form-data).",
)
async def upload_videos_multipart(
    videos: list[UploadFile] = File(...),
    settings: Settings = Depends(get_settings),
) -> dict:
    if not videos:
        raise HTTPException(status_code=400, detail="Cần ít nhất một video.")

    upload_dir = Path(settings.resolved_data_root()) / "videos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for video in videos:
        name = Path(video.filename or "video.mp4").name
        if Path(name).suffix.lower() not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400, detail=f"{name}: extension không hỗ trợ."
            )

        target = upload_dir / name
        with target.open("wb") as out:
            while chunk := await video.read(1024 * 1024):
                out.write(chunk)
        saved.append({"name": name, "size": target.stat().st_size})
    return {"count": len(saved), "videos": saved}
