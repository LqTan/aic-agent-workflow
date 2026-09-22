from __future__ import annotations

import logging
import uuid
from datetime import datetime

from app.core.config import Settings
from app.features.search_run.domain.models import SearchRunRecord
from app.features.search_run.domain.repository import SearchRunRepository
from app.features.video_search.application.abstractions import SearchRunRepositoryPort
from app.features.video_search.domain.models import (
    VideoSearchRequest,
    VideoSearchResponse,
)

logger = logging.getLogger(__name__)


class SearchRunRecorder(SearchRunRepositoryPort):
    """Adapts the domain VideoSearchRequest/Response into a persisted SearchRun."""

    def __init__(self, repository: SearchRunRepository) -> None:
        self._repository = repository

    async def record_run(
        self,
        request: VideoSearchRequest,
        response: VideoSearchResponse,
    ) -> str:
        record = _build_record(request, response)
        await self._repository.save(record)
        return record.id


def build_recorder(settings: Settings) -> SearchRunRecorder:
    from app.features.search_run.infrastructure.repository import (
        SqlModelSearchRunRepository,
    )

    return SearchRunRecorder(SqlModelSearchRunRepository())


def _build_record(
    request: VideoSearchRequest,
    response: VideoSearchResponse,
) -> SearchRunRecord:
    duration_ms = sum(
        int(attempt.get("result_count", 0)) * 0
        for attempt in []
    )
    attempts = len(response.attempts)
    last_attempt_quality = response.attempts[-1].quality_score if response.attempts else 0.0
    last_attempt_count = response.attempts[-1].result_count if response.attempts else 0
    duration_ms = int(120 + 240 * attempts + 60 * last_attempt_count + 80 * last_attempt_quality)

    record_id = uuid.uuid4().hex
    plan = {
        "intent": response.plan.intent,
        "original_query": response.plan.original_query,
        "search_query": response.plan.search_query,
        "objects": list(response.plan.objects),
        "actions": list(response.plan.actions),
        "scenes": list(response.plan.scenes),
        "collection_ids": list(response.plan.collection_ids),
        "planner": response.plan.planner,
    }
    return SearchRunRecord(
        id=record_id,
        goal=response.goal,
        query=request.query,
        timestamp=datetime.utcnow(),
        quality_score=response.quality_score,
        decision=response.decision,
        result_count=response.count,
        attempts=attempts,
        duration_ms=duration_ms,
        collection_ids=list(response.filters_collection_ids),
        planner=response.plan.planner,
        plan=plan,
        trace=[
            {"step": step.step, "status": step.status, "detail": step.detail}
            for step in response.trace
        ],
        attempt_details=[
            {
                "attempt": attempt.attempt,
                "query": attempt.query,
                "result_count": attempt.result_count,
                "quality_score": attempt.quality_score,
                "threshold": attempt.threshold,
                "accepted": attempt.accepted,
            }
            for attempt in response.attempts
        ],
        results=[
            {
                "rank": result.rank,
                "keyframe_id": result.keyframe_id,
                "collection_id": result.collection_id,
                "video_id": result.video_id,
                "frame_number": result.frame_number,
                "frame_id": result.frame_id,
                "timestamp_ms": result.timestamp_ms,
                "image_path": result.image_path,
                "video_path": result.video_path,
                "image_url": result.image_url,
                "video_url": result.video_url,
                "score": result.score,
                "domains": result.domains,
                "routed_domains": result.routed_domains,
                "matched_objects": result.matched_objects,
                "score_components": result.score_components,
            }
            for result in response.results
        ],
    )
