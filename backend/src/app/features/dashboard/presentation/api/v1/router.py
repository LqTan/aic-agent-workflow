from __future__ import annotations

from fastapi import APIRouter

from app.features.dashboard.application.use_cases.aggregate import build_overview

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", summary="Aggregate stats for the dashboard")
async def dashboard_overview() -> dict:
    return build_overview()
