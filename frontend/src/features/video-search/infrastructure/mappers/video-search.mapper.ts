import { VideoSearchRequest, VideoSearchResponse } from "../../domain/models/video-search.model";
import { VideoSearchRequestDto, VideoSearchResponseDto } from "../dtos/video-search.dto";
import { LocalSearchResponseDto } from "../dtos/local-search.dto";

export class VideoSearchMapper {
    static toReqestDto(
        request: VideoSearchRequest,
    ): VideoSearchRequestDto {
        return {
            query: request.query,
            collection_ids: request.collectionIds,
            top_k: request.topK,
            quality_threshold: request.qualityThreshold,
            max_attempts: request.maxAttempts,
        };
    }

    static toDomain(
        dto: VideoSearchResponseDto,
    ): VideoSearchResponse {
        return {
            goal: dto.goal,

            plan: {
                intent: dto.plan.intent,
                originalQuery: dto.plan.original_query,
                searchQuery: dto.plan.search_query,
                objects: dto.plan.objects,
                actions: dto.plan.actions,
                scenes: dto.plan.scenes,
                collectionIds: dto.plan.collection_ids,
                planner: dto.plan.planner,
            },

            attempts: dto.attempts.map((attempt) => ({
                attempt: attempt.attempt,
                query: attempt.query,
                resultCount: attempt.result_count,
                qualityScore: attempt.quality_score,
                threshold: attempt.threshold,
                accepted: attempt.accepted,
            })),

            trace: dto.trace.map((trace) => ({
                step: trace.step,
                status: trace.status,
                detail: trace.detail,
            })),

            decision: dto.decision,
            qualityScore: dto.quality_score,
            count: dto.count,

            results: dto.results.map((result) => ({
                rank: result.rank,
                keyframeId: result.keyframe_id,
                collectionId: result.collection_id,
                videoId: result.video_id,
                frameNumber: result.frame_number,
                frameId: result.frame_id,
                timestampMs: result.timestamp_ms,
                imageUrl: result.image_url,
                videoUrl: result.video_url,
                score: result.score,
                domains: result.domains ?? [],
                routeDomains: result.routed_domains ?? [],
                matchesObjects: result.matched_objects ?? [],

                scoreComponents: result.score_components
                    ? {
                        clip: result.score_components.clip,
                        objectBow: result.score_components.object_bow,
                        domain: result.score_components.domain,
                    }
                    : undefined,
            })),
        };
    }

    /**
     * Wrap the local FastAPI backend's `/kis/search/` response (a flat list
     * of keyframe hits) into the shape the rest of the frontend expects.
     */
    static fromLocalSearch(
        dto: LocalSearchResponseDto,
    ): VideoSearchResponse {
        const topScore = dto.results[0]?.score ?? 0;
        const qualityThreshold = 0.42;

        return {
            goal: dto.query,

            plan: {
                intent: dto.query,
                originalQuery: dto.query,
                searchQuery: dto.query,
                objects: [],
                actions: [],
                scenes: [],
                collectionIds: [],
                planner: "local-clip",
            },

            attempts: [
                {
                    attempt: 1,
                    query: dto.query,
                    resultCount: dto.count,
                    qualityScore: topScore,
                    threshold: qualityThreshold,
                    accepted: dto.count > 0 && topScore >= qualityThreshold,
                },
            ],

            trace: [
                {
                    step: "local-search",
                    status: "completed",
                    detail: { count: dto.count, query: dto.query },
                },
            ],

            decision: dto.count > 0 ? "accepted" : "best_effort",
            qualityScore: topScore,
            count: dto.count,

            results: dto.results.map((result) => ({
                rank: result.rank,
                keyframeId: result.keyframe_id,
                collectionId: result.collection_id,
                videoId: result.video_id,
                frameNumber: result.frame_number,
                frameId: result.frame_id,
                timestampMs: result.timestamp_ms,
                imageUrl: result.image_url,
                videoUrl: result.video_url,
                score: result.score,
                domains: [],
                routeDomains: [],
                matchesObjects: [],
            })),
        };
    }
}
