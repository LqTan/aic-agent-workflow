import type {
    AgentSearchRequest,
    AgentSearchResponse,
} from "../../domain/models/agent-search.model";
import type { AgentSearchService } from "../../application/abstractions/agent-search-service.interface";

const N8N_WEBHOOK_URL =
    process.env.NEXT_PUBLIC_N8N_WEBHOOK_URL ??
    "http://localhost:5678/webhook/aic-agent-search";

export class N8nAgentSearchService implements AgentSearchService {
    async search(request: AgentSearchRequest): Promise<AgentSearchResponse> {
        const payload = JSON.stringify({
            query: request.query,
            top_k: request.topK ?? 6,
            max_attempts: request.maxAttempts ?? 2,
            _ts: Date.now(),
        });
        console.log("[n8n] POST", N8N_WEBHOOK_URL, payload);
        const startedAt = performance.now();

        const response = await fetch(N8N_WEBHOOK_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payload,
            cache: "no-store",
        });

        const elapsed = Math.round(performance.now() - startedAt);
        console.log(
            "[n8n] response",
            response.status,
            `trong ${elapsed}ms`,
        );

        if (!response.ok) {
            const text = await response.text();
            throw new Error(
                `n8n webhook lỗi ${response.status}: ${text.slice(0, 200)}`,
            );
        }

        const raw = (await response.json()) as Record<string, unknown>;
        return normalize(raw);
    }
}

function normalize(raw: Record<string, unknown>): AgentSearchResponse {
    const plan = (raw.plan ?? {}) as Record<string, unknown>;

    return {
        id: typeof raw.id === "string" ? raw.id : undefined,
        goal: String(raw.goal ?? ""),
        plan: {
            intent: String(plan.intent ?? ""),
            originalQuery: String(plan.original_query ?? ""),
            searchQuery: String(plan.search_query ?? ""),
            objects: toStringArray(plan.objects),
            actions: toStringArray(plan.actions),
            scenes: toStringArray(plan.scenes),
            collectionIds: toStringArray(plan.collection_ids),
            planner: String(plan.planner ?? ""),
        },
        attempts: toAttempts(raw.attempts),
        trace: toTrace(raw.trace ?? raw.attempt_details),
        decision:
            raw.decision === "accepted" ? "accepted" : "best_effort",
        qualityScore: Number(raw.quality_score ?? 0),
        resultCount: Number(raw.result_count ?? raw.count ?? 0),
        durationMs: Number(raw.duration_ms ?? 0),
        planner: String(raw.planner ?? plan.planner ?? ""),
        results: toResults(raw.results),
    };
}

function toStringArray(value: unknown): string[] {
    return Array.isArray(value) ? value.map((v) => String(v)) : [];
}

function toAttempts(value: unknown): AgentSearchResponse["attempts"] {
    if (!Array.isArray(value)) return [];
    return value.map((item) => {
        const v = item as Record<string, unknown>;
        return {
            attempt: Number(v.attempt ?? 0),
            query: String(v.query ?? ""),
            resultCount: Number(v.result_count ?? 0),
            qualityScore: Number(v.quality_score ?? 0),
            threshold: Number(v.threshold ?? 0),
            accepted: Boolean(v.accepted),
        };
    });
}

function toTrace(value: unknown): AgentSearchResponse["trace"] {
    if (!Array.isArray(value)) return [];
    return value.map((item) => {
        const v = item as Record<string, unknown>;
        return {
            step: String(v.step ?? ""),
            status: String(v.status ?? ""),
            detail: (v.detail as Record<string, unknown>) ?? {},
        };
    });
}

function toResults(value: unknown): AgentSearchResponse["results"] {
    if (!Array.isArray(value)) return [];
    return value.map((item, index) => {
        const v = item as Record<string, unknown>;
        const scoreComponents = v.score_components as
            | Record<string, unknown>
            | undefined;
        return {
            rank: Number(v.rank ?? index + 1),
            keyframeId: String(v.keyframe_id ?? ""),
            collectionId: String(v.collection_id ?? ""),
            videoId: String(v.video_id ?? ""),
            frameNumber: Number(v.frame_number ?? 0),
            frameId: Number(v.frame_id ?? 0),
            timestampMs: Number(v.timestamp_ms ?? 0),
            imageUrl: String(v.image_url ?? ""),
            videoUrl: String(v.video_url ?? ""),
            score: Number(v.score ?? 0),
            domains: toStringArray(v.domains),
            routedDomains: toStringArray(v.routed_domains),
            matchedObjects: toStringArray(v.matched_objects),
            scoreComponents: scoreComponents
                ? {
                      clip: Number(scoreComponents.clip ?? 0),
                      objectBow: Number(scoreComponents.object_bow ?? 0),
                      domain: Number(scoreComponents.domain ?? 0),
                  }
                : undefined,
        };
    });
}