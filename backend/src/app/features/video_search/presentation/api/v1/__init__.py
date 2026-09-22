from __future__ import annotations

from fastapi import APIRouter

from app.features.video_search.presentation.api.v1.router import router as kis_router
from app.features.video_search.presentation.api.v1.tools_router import router as tools_router

router = APIRouter()
router.include_router(kis_router)
router.include_router(tools_router)
