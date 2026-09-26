export interface AgentSearchRequest {
    query: string;
    topK?: number;
    maxAttempts?: number;
}

export interface AgentSearchPlan {
    intent: string;
    originalQuery: string;
    searchQuery: string;
    objects: string[];
    actions: string[];
    scenes: string[];
    collectionIds: string[];
    planner: string;
}

export interface AgentAttempt {
    attempt: number;
    query: string;
    resultCount: number;
    qualityScore: number;
    threshold: number;
    accepted: boolean;
}

export interface AgentTraceStep {
    step: string;
    status: string;
    detail: Record<string, unknown>;
}

export interface AgentResult {
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
    routedDomains: string[];
    matchedObjects: string[];
    scoreComponents?: {
        clip: number;
        objectBow: number;
        domain: number;
    };
}

export interface AgentSearchResponse {
    id?: string;
    goal: string;
    plan: AgentSearchPlan;
    attempts: AgentAttempt[];
    trace: AgentTraceStep[];
    decision: "accepted" | "best_effort";
    qualityScore: number;
    resultCount: number;
    durationMs: number;
    planner: string;
    results: AgentResult[];
}