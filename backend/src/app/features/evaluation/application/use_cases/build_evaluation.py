from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from app.features.search_run.infrastructure.orm import SearchRunORM
from app.shared.db.session import get_engine


@dataclass(frozen=True)
class EvaluationOverview:
    totalRuns: int
    averageQuality: float
    averageAttempts: float
    averageLatency: float
    thresholdDefault: float
    decisionDistribution: dict
    qualityDistribution: list[dict]
    runs: list[dict]


QUALITY_BUCKETS = [
    ("0-20%", 0.0, 0.2),
    ("20-40%", 0.2, 0.4),
    ("40-60%", 0.4, 0.6),
    ("60-80%", 0.6, 0.8),
    ("80-100%", 0.8, 1.01),
]


def build_evaluation(threshold: float = 0.42) -> dict:
    with Session(get_engine()) as session:
        rows = session.exec(select(SearchRunORM).order_by(SearchRunORM.timestamp.desc())).all()

    total = len(rows)
    quality_total = sum(row.quality_score for row in rows)
    attempts_total = sum(row.attempts for row in rows)
    latency_total = sum(row.duration_ms for row in rows)
    distribution = {"accepted": 0, "bestEffort": 0}
    buckets = {label: 0 for label, *_ in QUALITY_BUCKETS}
    for row in rows:
        distribution[row.decision if row.decision in distribution else "bestEffort"] += 1
        for label, min_score, max_score in QUALITY_BUCKETS:
            if min_score <= row.quality_score < max_score:
                buckets[label] += 1
                break

    quality_distribution = [
        {"bucket": label, "min": min_s, "max": max_s, "count": buckets[label]}
        for label, min_s, max_s in QUALITY_BUCKETS
    ]

    runs_payload = [
        {
            "id": row.id,
            "goal": row.goal,
            "query": row.query,
            "timestamp": row.timestamp.isoformat(),
            "qualityScore": row.quality_score,
            "threshold": threshold,
            "attempts": row.attempts,
            "decision": row.decision,
            "resultCount": row.result_count,
            "latencyMs": row.duration_ms,
            "collectionIds": list(row.collection_ids or []),
        }
        for row in rows
    ]

    return {
        "totalRuns": total,
        "averageQuality": round(quality_total / total, 4) if total else 0.0,
        "averageAttempts": round(attempts_total / total, 2) if total else 0.0,
        "averageLatency": int(latency_total / total) if total else 0,
        "thresholdDefault": threshold,
        "decisionDistribution": distribution,
        "qualityDistribution": quality_distribution,
        "runs": runs_payload,
    }
