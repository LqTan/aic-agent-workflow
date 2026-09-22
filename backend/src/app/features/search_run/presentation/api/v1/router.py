from __future__ import annotations

from fastapi import APIRouter

from app.core.errors import RunNotFound
from app.features.search_run.infrastructure.repository import (
    SqlModelSearchRunRepository,
)

router = APIRouter(prefix="/runs", tags=["Search Runs"])


@router.get("/{run_id}", summary="Fetch a single search run by id")
async def get_run(run_id: str) -> dict:
    repository = SqlModelSearchRunRepository()
    record = await repository.get(run_id)
    if record is None:
        raise RunNotFound(f"Run {run_id} không tồn tại.")
    return _serialize(record)


@router.get("/", summary="List recent search runs (newest first)")
async def list_runs(limit: int = 50) -> dict:
    repository = SqlModelSearchRunRepository()
    records = await repository.list_recent(limit=limit)
    return {"total": len(records), "runs": [_summary(record) for record in records]}


def _serialize(record) -> dict:
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
        "results": record.results,
    }


def _summary(record) -> dict:
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
    }
