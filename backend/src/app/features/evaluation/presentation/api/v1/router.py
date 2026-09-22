from __future__ import annotations

from fastapi import APIRouter

from app.features.evaluation.application.use_cases.build_evaluation import (
    build_evaluation,
)

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/overview", summary="Retrieval/model evaluation overview")
async def evaluation_overview() -> dict:
    return build_evaluation()
