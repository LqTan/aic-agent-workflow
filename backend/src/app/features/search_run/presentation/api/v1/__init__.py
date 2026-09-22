from __future__ import annotations

from fastapi import APIRouter

from app.features.search_run.presentation.api.v1.router import router as runs_router

router = APIRouter()
router.include_router(runs_router)
