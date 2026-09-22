from __future__ import annotations

from fastapi import APIRouter

from app.features.evaluation.presentation.api.v1.router import router as evaluation_router

router = APIRouter()
router.include_router(evaluation_router)
