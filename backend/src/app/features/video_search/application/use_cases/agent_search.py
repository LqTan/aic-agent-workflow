from __future__ import annotations

from dataclasses import asdict

from app.core.errors import SearchServiceFailed, SearchServiceUnavailable
from app.features.video_search.application.abstractions import (
    PlannerPort,
    SearchEnginePort,
    SearchRunRepositoryPort,
)
from app.features.video_search.application.services.agent import run_agent
from app.features.video_search.application.use_cases.search import _to_result
from app.features.video_search.domain.models import VideoSearchRequest


class AgentSearchUseCase:
    """Planner → retrieve → evaluate → rewrite/retry orchestration."""

    def __init__(
        self,
        *,
        engine: SearchEnginePort,
        planner: PlannerPort,
        run_repository: SearchRunRepositoryPort | None = None,
    ) -> None:
        self._engine = engine
        self._planner = planner
        self._run_repository = run_repository

    async def execute(self, request: VideoSearchRequest) -> dict:
        try:
            agent_output = run_agent(
                query=request.query,
                collection_ids=request.collection_ids,
                top_k=request.top_k,
                quality_threshold=request.quality_threshold,
                max_attempts=request.max_attempts,
                search_tool=self._engine.search,
                planner=self._planner.plan,
            )
        except SearchServiceUnavailable:
            raise
        except Exception as exc:
            raise SearchServiceFailed(str(exc) or "Agent gặp lỗi.") from exc

        response = agent_output["response"]
        results = [_to_result(item, request.top_k) for item in agent_output["raw_results"]]
        count = len(results)

        payload = {
            "goal": response.goal,
            "plan": asdict(response.plan),
            "attempts": [asdict(attempt) for attempt in response.attempts],
            "trace": [asdict(step) for step in response.trace],
            "decision": response.decision,
            "quality_score": response.quality_score,
            "filters": {"collection_ids": response.filters_collection_ids},
            "count": count,
            "results": [asdict(result) for result in results],
        }

        record_id: str | None = None
        if self._run_repository is not None:
            response_with_results = response.__class__(
                goal=response.goal,
                plan=response.plan,
                attempts=response.attempts,
                trace=response.trace,
                decision=response.decision,
                quality_score=response.quality_score,
                count=count,
                results=results,
                filters_collection_ids=response.filters_collection_ids,
            )
            record_id = await self._run_repository.record_run(
                request, response_with_results
            )

        if record_id is not None:
            payload["id"] = record_id

        return payload
