from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import Settings, get_settings
from app.core.errors import InvalidSearchRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kis/tools", tags=["KIS Tools"])

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@router.post("/planner", summary="Build a SearchPlan for a query (n8n tool)")
async def planner_tool(payload: dict) -> dict:
    from app.features.video_search.dependency_injection import build_planner

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
async def retrieval_tool(payload: dict, request_timing: dict | None = None) -> dict:
    from app.features.video_search.dependency_injection import build_engine

    query = (payload.get("query") or "").strip()
    if not query:
        raise InvalidSearchRequest("Query không được rỗng.")
    engine = build_engine(get_settings())
    collection_ids = list(payload.get("collection_ids") or [])
    top_k = int(payload.get("top_k") or 12)
    parsed, results = engine.search(
        query=query, collection_ids=collection_ids, top_k=top_k
    )
    return {
        "parsed": parsed,
        "results": results,
        "result_count": len(results),
    }


@router.post("/validation", summary="Score candidate results against a plan (n8n tool)")
async def validation_tool(payload: dict) -> dict:
    from app.features.video_search.application.services.agent import evaluate_results
    from app.features.video_search.domain.models import SearchPlan

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
    from app.features.video_search.application.services.agent import refine_query
    from app.features.video_search.domain.models import SearchPlan

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
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload one or more videos (n8n tool)",
)
async def upload_videos(
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
            raise HTTPException(status_code=400, detail=f"{name}: extension không hỗ trợ.")

        target = upload_dir / name
        with target.open("wb") as out:
            while chunk := await video.read(1024 * 1024):
                out.write(chunk)
        saved.append({"name": name, "size": target.stat().st_size})
    return {"count": len(saved), "videos": saved}
