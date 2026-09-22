from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

COLLECTION_ID_PATTERN = re.compile(r"^L\d+$")


class VideoSearchRequestSchema(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    collection_ids: list[str] = Field(default_factory=list, max_length=50)
    top_k: int = Field(default=100, ge=1, le=100)
    quality_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    max_attempts: int | None = Field(default=None, ge=1, le=3)

    @field_validator("collection_ids")
    @classmethod
    def _validate_collection_ids(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for value in values:
            normalized = value.strip().upper()
            if not COLLECTION_ID_PATTERN.fullmatch(normalized):
                raise ValueError(f"Collection ID không hợp lệ: {value}. Ví dụ đúng: L21.")
            if normalized not in cleaned:
                cleaned.append(normalized)
        return cleaned


class AgentSearchRequestSchema(VideoSearchRequestSchema):
    top_k: int = Field(default=12, ge=1, le=50)
    quality_threshold: float = Field(default=0.42, ge=0.0, le=1.0)
    max_attempts: int = Field(default=2, ge=1, le=3)


class ScoreComponentsSchema(BaseModel):
    clip: float = 0.0
    object_bow: float = 0.0
    domain: float = 0.0


class VideoSearchResultSchema(BaseModel):
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
    domains: list[str] = Field(default_factory=list)
    routed_domains: list[str] = Field(default_factory=list)
    matched_objects: list[str] = Field(default_factory=list)
    score_components: ScoreComponentsSchema | None = None


class VideoSearchResponseSchema(BaseModel):
    query: str
    parsed_keys: list[str]
    filters: dict
    count: int
    results: list[VideoSearchResultSchema]


class AgentAttemptSchema(BaseModel):
    attempt: int
    query: str
    result_count: int
    quality_score: float
    threshold: float
    accepted: bool


class AgentTraceStepSchema(BaseModel):
    step: str
    status: str
    detail: dict


class AgentSearchPlanSchema(BaseModel):
    intent: str
    original_query: str
    search_query: str
    objects: list[str]
    actions: list[str]
    scenes: list[str]
    collection_ids: list[str]
    planner: str


class AgentSearchResponseSchema(BaseModel):
    goal: str
    plan: AgentSearchPlanSchema
    attempts: list[AgentAttemptSchema]
    trace: list[AgentTraceStepSchema]
    decision: str
    quality_score: float
    filters: dict
    count: int
    results: list[VideoSearchResultSchema]


class InspectResponseSchema(BaseModel):
    query: str
    parsed_keys: list[str]
    filters: dict
    clip_query: str
    analysis: dict
    routing: dict
    candidate_trace: dict
    index: dict
