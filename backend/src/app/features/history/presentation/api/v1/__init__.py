from __future__ import annotations

from fastapi import APIRouter

from app.features.history.presentation.api.v1.router import router as history_router

router = APIRouter()
router.include_router(history_router)
