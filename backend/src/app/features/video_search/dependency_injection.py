from __future__ import annotations

from app.core.config import Settings
from app.features.video_search.application.abstractions import (
    PlannerPort,
    SearchEnginePort,
    SearchRunRepositoryPort,
)
from app.features.video_search.application.use_cases.agent_search import (
    AgentSearchUseCase,
)
from app.features.video_search.application.use_cases.search import (
    InspectUseCase,
    SearchUseCase,
)
from app.features.video_search.infrastructure.planners.llm_planner import LlmPlanner
from app.features.video_search.infrastructure.planners.local_planner import LocalPlanner
from app.features.video_search.infrastructure.search_engine.hybrid_adapter import (
    HybridSearchEngineAdapter,
)


def build_planner(settings: Settings) -> PlannerPort:
    llm = LlmPlanner(settings)
    return llm if llm.is_available() else LocalPlanner()


def build_engine(settings: Settings) -> SearchEnginePort:
    return HybridSearchEngineAdapter(settings)


def build_search_use_case(settings: Settings) -> SearchUseCase:
    return SearchUseCase(build_engine(settings))


def build_inspect_use_case(settings: Settings) -> InspectUseCase:
    return InspectUseCase(build_engine(settings))


def build_run_recorder(settings: Settings) -> SearchRunRepositoryPort:
    from app.features.search_run.infrastructure.recorder import build_recorder

    return build_recorder(settings)


def build_agent_use_case(
    settings: Settings,
    run_repository: SearchRunRepositoryPort | None = None,
) -> AgentSearchUseCase:
    return AgentSearchUseCase(
        engine=build_engine(settings),
        planner=build_planner(settings),
        run_repository=run_repository or build_run_recorder(settings),
    )
