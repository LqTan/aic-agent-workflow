from __future__ import annotations

from collections.abc import Iterable

from sqlmodel import Session, select

from app.features.search_run.domain.models import SearchRunRecord
from app.features.search_run.domain.repository import SearchRunRepository
from app.features.search_run.infrastructure.orm import SearchRunORM
from app.shared.db.session import get_engine


class SqlModelSearchRunRepository(SearchRunRepository):
    """SQLModel-backed implementation. Works with SQLite or Postgres."""

    async def save(self, record: SearchRunRecord) -> None:
        orm = SearchRunORM(
            id=record.id,
            goal=record.goal,
            query=record.query,
            timestamp=record.timestamp,
            quality_score=record.quality_score,
            decision=record.decision,
            result_count=record.result_count,
            attempts=record.attempts,
            duration_ms=record.duration_ms,
            collection_ids=record.collection_ids,
            planner=record.planner,
            plan=record.plan,
            trace=record.trace,
            attempt_details=record.attempt_details,
            results=record.results,
        )
        with Session(get_engine()) as session:
            session.add(orm)
            session.commit()

    async def get(self, run_id: str) -> SearchRunRecord | None:
        with Session(get_engine()) as session:
            orm = session.get(SearchRunORM, run_id)
            return _to_record(orm) if orm else None

    async def list_recent(self, *, limit: int = 50) -> list[SearchRunRecord]:
        with Session(get_engine()) as session:
            statement = (
                select(SearchRunORM)
                .order_by(SearchRunORM.timestamp.desc())
                .limit(limit)
            )
            return [_to_record(orm) for orm in session.exec(statement).all()]

    async def count(self) -> int:
        with Session(get_engine()) as session:
            return len(session.exec(select(SearchRunORM)).all())

    async def aggregate(self) -> dict:
        with Session(get_engine()) as session:
            rows: Iterable[SearchRunORM] = session.exec(select(SearchRunORM)).all()
            return _aggregate(rows)


def _to_record(orm: SearchRunORM) -> SearchRunRecord:
    return SearchRunRecord(
        id=orm.id,
        goal=orm.goal,
        query=orm.query,
        timestamp=orm.timestamp,
        quality_score=orm.quality_score,
        decision=orm.decision,
        result_count=orm.result_count,
        attempts=orm.attempts,
        duration_ms=orm.duration_ms,
        collection_ids=list(orm.collection_ids or []),
        planner=orm.planner,
        plan=dict(orm.plan or {}),
        trace=list(orm.trace or []),
        attempt_details=list(orm.attempt_details or []),
        results=list(orm.results or []),
    )


def _aggregate(rows: Iterable[SearchRunORM]) -> dict:
    accepted = 0
    best_effort = 0
    quality_total = 0.0
    attempts_total = 0
    latency_total = 0
    total = 0
    for orm in rows:
        total += 1
        if orm.decision == "accepted":
            accepted += 1
        else:
            best_effort += 1
        quality_total += orm.quality_score
        attempts_total += orm.attempts
        latency_total += orm.duration_ms
    return {
        "total": total,
        "accepted": accepted,
        "best_effort": best_effort,
        "average_quality": round(quality_total / total, 4) if total else 0.0,
        "average_attempts": round(attempts_total / total, 2) if total else 0.0,
        "average_latency_ms": int(latency_total / total) if total else 0,
    }
