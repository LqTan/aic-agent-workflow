import { VdieoSearchResponse, VideoSearchRequest } from "../../domain/models/video-search.model";
import { VideoSearchRequestDto, VideoSearchResponseDto } from "../dtos/video-search.dto";

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
    ): VdieoSearchResponse {
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
}
