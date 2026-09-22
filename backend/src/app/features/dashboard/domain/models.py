from __future__ import annotations

from datetime import datetime


class DashboardOverview:
    """Plain dashboard aggregate. Implementation lives in services/aggregate.py."""

    totalQueries: int
    acceptedQueries: int
    bestEffortQueries: int
    averageQualityScore: float
    averageAttempts: float
    averageDurationMs: int
    recentRuns: list[dict]
    qualityTrend: list[dict]
    lastUpdatedAt: datetime
