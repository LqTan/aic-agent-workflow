from __future__ import annotations

from fastapi import APIRouter

from app.features.dashboard.presentation.api.v1.router import router as dashboard_router

router = APIRouter()
router.include_router(dashboard_router)
