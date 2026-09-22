export interface VideoSearchRequest {
    query: string;
    collectionIds?: string[];
    topK?: number;
    qualityThreshold?: number;
    maxAttempts?: number;
}

export interface SearchPlan {
    intent: string;
    originalQuery: string;
    searchQuery: string;
    objects: string[];
    actions: string[];
    scenes: string[];
    collectionIds: string[];
    planner: string;
}

export interface SearchAttempt {
    attempt: number;
    query: string;
    resultCount: number;
    qualityScore: number;
    threshold: number;
    accepted: boolean;
}

export interface ScoreComponents {
    clip: number;
    objectBow: number;
    domain: number;
}

export interface VideoSearchResult {
    rank: number;
    keyframeId: string;
    collectionId: string;
    videoId: string;
    frameNumber: number;
    frameId: number;
    timestampMs: number;
    imageUrl: string;
    videoUrl: string;
    score: number;
    domains: string[];
    routeDomains: string[];
    matchesObjects: string[];
    scoreComponents?: ScoreComponents;
}

export interface AgentTrace {
    step: string;
    status: string;
    detail: Record<string, unknown>;
}

export interface VideoSearchResponse {
    goal: string;
    plan: SearchPlan;
    attempts: SearchAttempt[];
    trace: AgentTrace[];
    decision: "accepted" | "best_effort";
    qualityScore: number;
    count: number;    
    results: VideoSearchResult[];
}
