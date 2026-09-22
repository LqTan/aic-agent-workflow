from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.features.search_run.infrastructure.orm import SearchRunORM
from app.shared.db.session import get_engine


def build_overview(limit: int = 7) -> dict:
    with Session(get_engine()) as session:
        rows = session.exec(select(SearchRunORM).order_by(SearchRunORM.timestamp.desc())).all()

    total = len(rows)
    accepted = sum(1 for row in rows if row.decision == "accepted")
    best_effort = total - accepted
    avg_quality = round(sum(row.quality_score for row in rows) / total, 4) if total else 0.0
    avg_attempts = round(sum(row.attempts for row in rows) / total, 2) if total else 0.0
    avg_latency = int(sum(row.duration_ms for row in rows) / total) if total else 0

    trend_map: dict[str, dict] = defaultdict(
        lambda: {"averageQualityScore": 0.0, "queryCount": 0, "_total": 0.0}
    )
    for row in rows:
        date = row.timestamp.date().isoformat()
        bucket = trend_map[date]
        bucket["_total"] += row.quality_score
        bucket["queryCount"] += 1

    today = datetime.utcnow().date()
    quality_trend: list[dict] = []
    for offset in range(limit - 1, -1, -1):
        date = (today - timedelta(days=offset)).isoformat()
        bucket = trend_map.get(date, {"_total": 0.0, "queryCount": 0})
        avg = round(bucket["_total"] / bucket["queryCount"], 4) if bucket["queryCount"] else 0.0
        quality_trend.append({
            "date": date,
            "averageQualityScore": avg,
            "queryCount": bucket["queryCount"],
        })

    return {
        "totalQueries": total,
        "acceptedQueries": accepted,
        "bestEffortQueries": best_effort,
        "averageQualityScore": avg_quality,
        "averageAttempts": avg_attempts,
        "averageDurationMs": avg_latency,
        "totalIndexedVideos": 0,
        "totalCollections": len({row.planner for row in rows}),
        "lastUpdatedAt": datetime.utcnow().isoformat(),
        "recentRuns": [
            {
                "id": row.id,
                "goal": row.goal,
                "query": row.query,
                "timestamp": row.timestamp.isoformat(),
                "qualityScore": row.quality_score,
                "attempts": row.attempts,
                "decision": row.decision,
                "resultCount": row.result_count,
                "durationMs": row.duration_ms,
            }
            for row in rows[:7]
        ],
        "qualityTrend": quality_trend,
    }
