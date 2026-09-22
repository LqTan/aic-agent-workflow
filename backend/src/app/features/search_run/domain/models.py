from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SearchRunRecord:
    id: str
    goal: str
    query: str
    timestamp: datetime
    quality_score: float
    decision: str  # "accepted" | "best_effort"
    result_count: int
    attempts: int
    duration_ms: int
    collection_ids: list[str]
    planner: str
    plan: dict
    trace: list[dict]
    attempt_details: list[dict]
    results: list[dict] = field(default_factory=list)
