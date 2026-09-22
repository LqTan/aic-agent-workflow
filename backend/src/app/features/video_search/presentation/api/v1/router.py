from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import Settings, get_settings
from app.features.video_search.application.use_cases.agent_search import (
    AgentSearchUseCase,
)
from app.features.video_search.application.use_cases.search import (
    InspectUseCase,
    SearchUseCase,
)
from app.features.video_search.dependency_injection import (
    build_agent_use_case,
    build_inspect_use_case,
    build_search_use_case,
)
from app.features.video_search.domain.models import VideoSearchRequest
from app.features.video_search.presentation.schemas import (
    AgentSearchRequestSchema,
    AgentSearchResponseSchema,
    InspectResponseSchema,
    VideoSearchRequestSchema,
    VideoSearchResponseSchema,
)
from app.features.video_search.presentation.url_builder import (
    format_results_with_urls,
    normalize_asset_path,
)

router = APIRouter(prefix="/kis", tags=["KIS"])


def get_search_use_case(
    settings: Settings = Depends(get_settings),
) -> SearchUseCase:
    return build_search_use_case(settings)


def get_inspect_use_case(
    settings: Settings = Depends(get_settings),
) -> InspectUseCase:
    return build_inspect_use_case(settings)


def get_agent_use_case(
    settings: Settings = Depends(get_settings),
) -> AgentSearchUseCase:
    return build_agent_use_case(settings)


@router.post(
    "/search/",
    response_model=VideoSearchResponseSchema,
    summary="Single-shot hybrid retrieval",
)
async def search_endpoint(
    payload: VideoSearchRequestSchema,
    request: Request,
    use_case: SearchUseCase = Depends(get_search_use_case),
    settings: Settings = Depends(get_settings),
) -> VideoSearchResponseSchema:
    video_request = VideoSearchRequest(
        query=payload.query,
        collection_ids=payload.collection_ids,
        top_k=payload.top_k,
    )
    response = use_case.execute(video_request)
    response["results"] = format_results_with_urls(
        results=response["results"],
        source=request,
    )
    return VideoSearchResponseSchema(**response)


@router.post(
    "/agent/search/",
    response_model=AgentSearchResponseSchema,
    summary="Agentic retrieval with planning, evaluation and retry",
)
async def agent_search_endpoint(
    payload: AgentSearchRequestSchema,
    request: Request,
    use_case: AgentSearchUseCase = Depends(get_agent_use_case),
    settings: Settings = Depends(get_settings),
) -> AgentSearchResponseSchema:
    video_request = VideoSearchRequest(
        query=payload.query,
        collection_ids=payload.collection_ids,
        top_k=payload.top_k,
        quality_threshold=payload.quality_threshold,
        max_attempts=payload.max_attempts,
    )
    response = await use_case.execute(video_request)
    response["results"] = format_results_with_urls(
        results=response["results"],
        source=request,
    )
    return AgentSearchResponseSchema(**response)


@router.post(
    "/search/inspect/",
    response_model=InspectResponseSchema,
    summary="Inspect KIS query routing and R-tree candidates",
)
async def inspect_endpoint(
    payload: VideoSearchRequestSchema,
    use_case: InspectUseCase = Depends(get_inspect_use_case),
) -> InspectResponseSchema:
    video_request = VideoSearchRequest(
        query=payload.query,
        collection_ids=payload.collection_ids,
        top_k=payload.top_k,
    )
    response = use_case.execute(video_request)
    return InspectResponseSchema(**response)


@router.get("/assets/{asset_path:path}", summary="Serve a KIS keyframe or video")
async def dataset_asset(asset_path: str, settings: Settings = Depends(get_settings)) -> FileResponse:
    relative = normalize_asset_path(asset_path)
    if relative is None:
        return JSONResponse(
            {"error": {"code": "invalid_asset", "message": "Asset không hợp lệ."}},
            status_code=404,
        )

    data_root = settings.resolved_data_root()
    target = (data_root / relative).resolve()

    if not target.is_file() or not target.is_relative_to(data_root):
        return JSONResponse(
            {"error": {"code": "asset_not_found", "message": "Asset không tồn tại."}},
            status_code=404,
        )

    media_type = "application/octet-stream"
    if target.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        media_type = f"image/{target.suffix.lstrip('.').lower()}"
    elif target.suffix.lower() == ".mp4":
        media_type = "video/mp4"

    return FileResponse(target, media_type=media_type)
