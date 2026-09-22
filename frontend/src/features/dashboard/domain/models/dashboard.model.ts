export interface SearchRunSummary {
    id: string;
    goal: string;
    query: string;
    timestamp: string;
    qualityScore: number;
    attempts: number;
    decision: "accepted" | "best_effort";
    resultCount: number;
    durationMs: number;
}

export interface QualityTrendPoint {
    date: string;
    averageQualityScore: number;
    queryCount: number;
}

export interface DashboardOverview {
    totalQueries: number;
    acceptedQueries: number;
    bestEffortQueries: number;
    averageQualityScore: number;
    averageAttempts: number;
    averageDurationMs: number;
    totalIndexedVideos: number;
    totalCollections: number;
    lastUpdatedAt: string;
    recentRuns: SearchRunSummary[];
    qualityTrend: QualityTrendPoint[];
}
