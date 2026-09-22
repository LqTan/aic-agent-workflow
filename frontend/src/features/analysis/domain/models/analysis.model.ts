import type { VideoSearchResponse } from "@/features/video-search/domain/models/video-search.model";

export type AnalysisDecision = "accepted" | "best_effort";

export interface AnalysisRunSummary {
    id: string;
    goal: string;
    query: string;
    timestamp: string;
    qualityScore: number;
    decision: AnalysisDecision;
    resultCount: number;
    attempts: number;
    durationMs: number;
    collectionIds: string[];
    planner: string;
}

export interface AnalysisList {
    total: number;
    runs: AnalysisRunSummary[];
}

export type AnalysisDetail = VideoSearchResponse;
