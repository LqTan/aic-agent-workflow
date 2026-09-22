from __future__ import annotations

from fastapi import APIRouter, Query

from app.features.history.application.use_cases.list_history import list_history

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/", summary="List recent search runs with optional filters")
async def get_history(
    decision: str | None = Query(default=None, pattern="^(accepted|best_effort|all)$"),
    query: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    return list_history(decision=decision, query=query, limit=limit)
