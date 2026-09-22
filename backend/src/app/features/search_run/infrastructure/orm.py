from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class SearchRunORM(SQLModel, table=True):
    __tablename__ = "search_runs"

    id: str = Field(primary_key=True, max_length=64)
    goal: str = Field(max_length=500, index=True)
    query: str = Field(max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    quality_score: float = Field(default=0.0)
    decision: str = Field(max_length=20, index=True)
    result_count: int = Field(default=0)
    attempts: int = Field(default=1)
    duration_ms: int = Field(default=0)
    collection_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    planner: str = Field(max_length=100)
    plan: dict = Field(default_factory=dict, sa_column=Column(JSON))
    trace: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    attempt_details: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    results: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
