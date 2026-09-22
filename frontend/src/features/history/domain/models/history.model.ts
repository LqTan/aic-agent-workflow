export type HistoryDecision = "accepted" | "best_effort";

export interface HistoryEntry {
    id: string;
    goal: string;
    query: string;
    timestamp: string;
    qualityScore: number;
    decision: HistoryDecision;
    resultCount: number;
    attempts: number;
    durationMs: number;
    collectionIds: string[];
}

export interface HistoryFilter {
    decision?: HistoryDecision | "all";
    query?: string;
}

export interface HistoryList {
    total: number;
    entries: HistoryEntry[];
}
