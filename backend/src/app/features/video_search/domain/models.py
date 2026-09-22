from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VideoSearchRequest:
    query: str
    collection_ids: list[str] = field(default_factory=list)
    top_k: int = 12
    quality_threshold: float = 0.42
    max_attempts: int = 2


@dataclass(frozen=True)
class SearchPlan:
    intent: str
    original_query: str
    search_query: str
    objects: tuple[str, ...]
    actions: tuple[str, ...]
    scenes: tuple[str, ...]
    collection_ids: tuple[str, ...]
    planner: str


@dataclass(frozen=True)
class SearchAttempt:
    attempt: int
    query: str
    result_count: int
    quality_score: float
    threshold: float
    accepted: bool


@dataclass(frozen=True)
class AgentTraceStep:
    step: str
    status: str
    detail: dict


@dataclass(frozen=True)
class VideoSearchResult:
    rank: int
    keyframe_id: str
    collection_id: str
    video_id: str
    frame_number: int
    frame_id: int
    timestamp_ms: int
    image_path: str
    video_path: str
    image_url: str
    video_url: str
    score: float
    domains: list[str] = field(default_factory=list)
    routed_domains: list[str] = field(default_factory=list)
    matched_objects: list[str] = field(default_factory=list)
    score_components: dict[str, float] | None = None


@dataclass(frozen=True)
class ParsedQuery:
    clean_query: str
    keys: list[str]
    collection_tags: list[str]
    effective_collection_ids: list[str]


@dataclass(frozen=True)
class VideoSearchResponse:
    goal: str
    plan: SearchPlan
    attempts: list[SearchAttempt]
    trace: list[AgentTraceStep]
    decision: str  # "accepted" | "best_effort"
    quality_score: float
    count: int
    results: list[VideoSearchResult]
    filters_collection_ids: list[str]
