"""Application-layer interfaces (ports) for the video_search feature."""

from __future__ import annotations

from typing import Protocol

from app.features.video_search.domain.models import (
    SearchPlan,
    VideoSearchRequest,
    VideoSearchResponse,
)


class PlannerPort(Protocol):
    """A planner produces a structured SearchPlan from a raw query."""

    name: str

    def plan(self, query: str, collection_ids: list[str]) -> SearchPlan: ...


class SearchEnginePort(Protocol):
    """A search engine returns ranked keyframes for a query."""

    def search(
        self,
        *,
        query: str,
        collection_ids: list[str],
        top_k: int,
    ) -> tuple[dict, list[dict]]: ...

    def inspect(
        self,
        *,
        query: str,
        collection_ids: list[str],
        top_k: int,
    ) -> tuple[dict, dict]: ...


class SearchRunRepositoryPort(Protocol):
    """Optional persistence hook used by the agent use case to log runs."""

    async def record_run(self, request: VideoSearchRequest, response: VideoSearchResponse) -> str: ...
