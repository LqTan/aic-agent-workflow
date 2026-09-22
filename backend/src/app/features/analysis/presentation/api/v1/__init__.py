from __future__ import annotations

from fastapi import APIRouter

from app.features.analysis.presentation.api.v1.router import router as analysis_router

router = APIRouter()
router.include_router(analysis_router)
