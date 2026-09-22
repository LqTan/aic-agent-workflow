export interface EvaluationRun {
    id: string;
    goal: string;
    query: string;
    timestamp: string;
    qualityScore: number;
    threshold: number;
    attempts: number;
    decision: "accepted" | "best_effort";
    resultCount: number;
    latencyMs: number;
    collectionIds: string[];
}

export interface QualityBucket {
    bucket: string;
    min: number;
    max: number;
    count: number;
}

export interface DecisionDistribution {
    accepted: number;
    bestEffort: number;
}

export interface EvaluationOverview {
    totalRuns: number;
    averageQuality: number;
    averageAttempts: number;
    averageLatency: number;
    thresholdDefault: number;
    decisionDistribution: DecisionDistribution;
    qualityDistribution: QualityBucket[];
    runs: EvaluationRun[];
}
