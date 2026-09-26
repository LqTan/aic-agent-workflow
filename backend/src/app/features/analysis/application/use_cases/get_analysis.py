from __future__ import annotations

from sqlmodel import Session, select

from app.core.config import get_settings
from app.features.search_run.infrastructure.orm import SearchRunORM
from app.features.video_search.presentation.url_builder import (
    build_asset_url_from_base,
)
from app.shared.db.session import get_engine


def list_runs(limit: int = 50) -> dict:
    with Session(get_engine()) as session:
        statement = select(SearchRunORM).order_by(SearchRunORM.timestamp.desc()).limit(limit)
        rows = session.exec(statement).all()
    return {
        "total": len(rows),
        "runs": [_summary(row) for row in rows],
    }


def get_run(run_id: str) -> dict | None:
    with Session(get_engine()) as session:
        row = session.get(SearchRunORM, run_id)
        if row is None:
            return None
    base_url = get_settings().app_public_base_url.rstrip("/")
    return {
        **_summary(row),
        "plan": row.plan,
        "trace": row.trace,
        "attemptDetails": row.attempt_details,
        "results": [_camel_result(item, base_url) for item in (row.results or [])],
    }


def _summary(row) -> dict:
    return {
        "id": row.id,
        "goal": row.goal,
        "query": row.query,
        "timestamp": row.timestamp.isoformat(),
        "qualityScore": row.quality_score,
        "decision": row.decision,
        "resultCount": row.result_count,
        "attempts": row.attempts,
        "durationMs": row.duration_ms,
        "collectionIds": list(row.collection_ids or []),
        "planner": row.planner,
    }


_RESULT_KEY_MAP = {
    "keyframe_id": "keyframeId",
    "collection_id": "collectionId",
    "video_id": "videoId",
    "frame_number": "frameNumber",
    "frame_id": "frameId",
    "timestamp_ms": "timestampMs",
    "image_path": "imagePath",
    "video_path": "videoPath",
    "image_url": "imageUrl",
    "video_url": "videoUrl",
    "matched_objects": "matchesObjects",
    "routed_domains": "routedDomains",
    "score_components": "scoreComponents",
}


def _camel_result(item: object, base_url: str) -> dict:
    """Map snake_case keys persisted by the agent pipeline to camelCase.

    Also rebuild ``imageUrl``/``videoUrl`` from ``imagePath``/``videoPath`` when
    the persisted URLs are empty (older runs predating the URL fix).
    """
    if not isinstance(item, dict):
        return {}
    mapped: dict = {}
    for key, value in item.items():
        camel = _RESULT_KEY_MAP.get(key, key)
        mapped[camel] = value
        if key == "matched_objects":
            mapped["matchedObjects"] = value

    if not mapped.get("imageUrl") and mapped.get("imagePath"):
        mapped["imageUrl"] = build_asset_url_from_base(base_url, mapped["imagePath"])
    if not mapped.get("videoUrl") and mapped.get("videoPath"):
        mapped["videoUrl"] = build_asset_url_from_base(base_url, mapped["videoPath"])
    return mapped
