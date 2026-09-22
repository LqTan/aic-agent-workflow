from __future__ import annotations

from sqlmodel import Session, select

from app.features.search_run.infrastructure.orm import SearchRunORM
from app.shared.db.session import get_engine


def list_runs(limit: int = 50) -> dict:
    with Session(get_engine()) as session:
        statement = select(SearchRunORM).order_by(SearchRunORM.timestamp.desc()).limit(limit)
        rows = session.exec(statement).all()
    return {
        "total": len(rows),
        "runs": [_summary(row) for row in rows],
    }


def get_run(run_id: str) -> dict | None:
    with Session(get_engine()) as session:
        row = session.get(SearchRunORM, run_id)
        if row is None:
            return None
    return {
        **_summary(row),
        "plan": row.plan,
        "trace": row.trace,
        "attemptDetails": row.attempt_details,
        "results": row.results,
    }


def _summary(row) -> dict:
    return {
        "id": row.id,
        "goal": row.goal,
        "query": row.query,
        "timestamp": row.timestamp.isoformat(),
        "qualityScore": row.quality_score,
        "decision": row.decision,
        "resultCount": row.result_count,
        "attempts": row.attempts,
        "durationMs": row.duration_ms,
        "collectionIds": list(row.collection_ids or []),
        "planner": row.planner,
    }
