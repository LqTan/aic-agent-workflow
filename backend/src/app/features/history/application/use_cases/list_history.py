from __future__ import annotations

from sqlmodel import Session, select

from app.features.search_run.infrastructure.orm import SearchRunORM
from app.shared.db.session import get_engine


def list_history(
    *,
    decision: str | None = None,
    query: str | None = None,
    limit: int = 100,
) -> dict:
    with Session(get_engine()) as session:
        statement = select(SearchRunORM).order_by(SearchRunORM.timestamp.desc()).limit(limit)
        rows = session.exec(statement).all()

    filtered = []
    for row in rows:
        if decision and decision != "all" and row.decision != decision:
            continue
        if query:
            lowered = query.lower()
            if lowered not in row.goal.lower() and lowered not in row.query.lower():
                continue
        filtered.append(row)

    return {
        "total": len(filtered),
        "entries": [
            {
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
            }
            for row in filtered
        ],
    }
