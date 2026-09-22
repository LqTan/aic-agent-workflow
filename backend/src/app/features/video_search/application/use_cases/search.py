from __future__ import annotations

import logging
from dataclasses import asdict

from app.core.errors import (
    SearchServiceFailed,
    SearchServiceUnavailable,
)
from app.features.video_search.application.abstractions import SearchEnginePort
from app.features.video_search.application.services.query_parser import parse_query
from app.features.video_search.domain.models import (
    VideoSearchRequest,
    VideoSearchResult,
)

logger = logging.getLogger(__name__)


class SearchUseCase:
    """Single-shot hybrid retrieval, no agent loop."""

    def __init__(self, engine: SearchEnginePort) -> None:
        self._engine = engine

    def execute(self, request: VideoSearchRequest) -> dict:
        parsed = parse_query(request.query, request.collection_ids)
        try:
            _, raw_results = self._engine.search(
                query=parsed.clean_query,
                collection_ids=parsed.effective_collection_ids,
                top_k=request.top_k,
            )
        except SearchServiceUnavailable:
            raise
        except Exception as exc:
            raise SearchServiceFailed(str(exc) or "Search engine gặp lỗi.") from exc

        if not isinstance(raw_results, list):
            raise SearchServiceFailed("Search engine phải trả về một list kết quả.")

        results = [_to_result(item, request.top_k) for item in raw_results[: request.top_k]]
        return {
            "query": request.query,
            "parsed_keys": parsed.keys,
            "filters": {"collection_ids": parsed.effective_collection_ids},
            "count": len(results),
            "results": [asdict(result) for result in results],
        }


class InspectUseCase:
    """Return the routing/trace of a query without ranking keyframes."""

    def __init__(self, engine: SearchEnginePort) -> None:
        self._engine = engine

    def execute(self, request: VideoSearchRequest) -> dict:
        parsed = parse_query(request.query, request.collection_ids)
        try:
            _, trace = self._engine.inspect(
                query=parsed.clean_query,
                collection_ids=parsed.effective_collection_ids,
                top_k=request.top_k,
            )
        except SearchServiceUnavailable:
            raise
        except Exception as exc:
            raise SearchServiceFailed(str(exc) or "Search engine gặp lỗi.") from exc

        if not isinstance(trace, dict):
            raise SearchServiceFailed("Search inspect phải trả về một object.")

        return {
            **trace,
            "query": request.query,
            "parsed_keys": parsed.keys,
            "filters": {"collection_ids": parsed.effective_collection_ids},
        }


def _to_result(raw: dict, top_k: int) -> VideoSearchResult:
    components = raw.get("score_components") or {}
    return VideoSearchResult(
        rank=int(raw.get("rank", 0)) or 1,
        keyframe_id=str(raw.get("keyframe_id", "")),
        collection_id=str(raw.get("collection_id", "")),
        video_id=str(raw.get("video_id", "")),
        frame_number=int(raw.get("frame_number", 0)),
        frame_id=int(raw.get("frame_id", raw.get("frame_number", 0))),
        timestamp_ms=int(raw.get("timestamp_ms", 0)),
        image_path=str(raw.get("image_path", "")),
        video_path=str(raw.get("video_path", "")),
        image_url="",
        video_url="",
        score=float(raw.get("score", 0.0)),
        domains=list(raw.get("domains", [])),
        routed_domains=list(raw.get("routed_domains", [])),
        matched_objects=list(raw.get("matched_objects", [])),
        score_components={
            "clip": float(components.get("clip", 0.0)),
            "object_bow": float(components.get("object_bow", 0.0)),
            "domain": float(components.get("domain", 0.0)),
        }
        if components
        else None,
    )
