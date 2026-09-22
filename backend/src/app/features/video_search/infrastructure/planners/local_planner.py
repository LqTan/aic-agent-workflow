from __future__ import annotations

from app.features.video_search.application.services.agent import local_plan
from app.features.video_search.domain.models import SearchPlan


class LocalPlanner:
    """Deterministic Vietnamese-aware planner. Used as the offline fallback."""

    name = "local"

    def plan(self, query: str, collection_ids: list[str]) -> SearchPlan:
        return local_plan(query, collection_ids)
