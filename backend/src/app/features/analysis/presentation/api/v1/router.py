from __future__ import annotations

from fastapi import APIRouter

from app.core.errors import RunNotFound
from app.features.analysis.application.use_cases.get_analysis import (
    get_run,
    list_runs,
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/runs", summary="List all runs with their summaries")
async def list_analysis_runs() -> dict:
    return list_runs()


@router.get("/runs/{run_id}", summary="Inspect a single run (plan, attempts, trace, results)")
async def get_analysis_run(run_id: str) -> dict:
    record = get_run(run_id)
    if record is None:
        raise RunNotFound(f"Run {run_id} không tồn tại.")
    return record
