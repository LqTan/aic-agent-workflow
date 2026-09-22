from __future__ import annotations

import csv
import threading
from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlmodel import Session, select

from app.core.config import get_settings
from app.features.search_run.infrastructure.orm import SearchRunORM
from app.shared.db.session import get_engine

_dataset_lock = threading.Lock()
_dataset_cache: dict[str, tuple[int, list[str]]] = {}


def _load_dataset_stats(manifest_path: Path) -> tuple[int, list[str]]:
    """Return ``(unique_video_count, sorted_unique_collection_ids)`` from manifest.csv."""
    if not manifest_path.is_file():
        return 0, []
    video_ids: set[str] = set()
    collection_ids: set[str] = set()
    with manifest_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("video_id"):
                video_ids.add(row["video_id"])
            if row.get("collection_id"):
                collection_ids.add(row["collection_id"])
    return len(video_ids), sorted(collection_ids)


def dataset_stats() -> tuple[int, list[str]]:
    settings = get_settings()
    manifest_path = Path(settings.resolved_data_root()) / "manifest.csv"
    cache_key = str(manifest_path)
    with _dataset_lock:
        cached = _dataset_cache.get(cache_key)
        if cached is not None:
            return cached
        stats = _load_dataset_stats(manifest_path)
        _dataset_cache[cache_key] = stats
        return stats


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

    today = datetime.now(UTC).date()
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

    # Dataset stats: prefer manifest (source of truth), fall back to persisted
    # run results when manifest is missing (e.g. demo mode, no dataset).
    total_videos, all_collections = dataset_stats()
    if total_videos == 0:
        total_videos, all_collections = _stats_from_persisted_results(rows)

    # Show only collections actually touched by recent runs plus the global
    # count, so the UI surfaces real activity without confusing totals.
    collections_touched = sorted(
        {c for row in rows for c in (row.collection_ids or [])}
    )
    total_collections = max(len(all_collections), len(collections_touched))

    return {
        "totalQueries": total,
        "acceptedQueries": accepted,
        "bestEffortQueries": best_effort,
        "averageQualityScore": avg_quality,
        "averageAttempts": avg_attempts,
        "averageDurationMs": avg_latency,
        "totalIndexedVideos": total_videos,
        "totalCollections": total_collections,
        "lastUpdatedAt": datetime.now(UTC).isoformat(),
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


def _stats_from_persisted_results(rows: Iterable[SearchRunORM]) -> tuple[int, list[str]]:
    video_ids: set[str] = set()
    collection_ids: set[str] = set()
    for row in rows:
        for result in row.results or []:
            video_id = result.get("video_id")
            collection_id = result.get("collection_id")
            if video_id:
                video_ids.add(video_id)
            if collection_id:
                collection_ids.add(collection_id)
    return len(video_ids), sorted(collection_ids)
