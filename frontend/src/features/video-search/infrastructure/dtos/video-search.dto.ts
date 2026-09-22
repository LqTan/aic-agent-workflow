export interface VideoSearchRequestDto {
    query: string;
    collection_ids?: string[];
    top_k?: number;
    quality_threshold?: number;
    max_attempts?: number;
}

export interface VideoSearchResponseDto {
    goal: string;

    plan: {
        intent: string;
        original_query: string;
        search_query: string;
        objects: string[];
        actions: string[];
        scenes: string[];
        collection_ids: string[];
        planner: string;
    };

    attempts: {
        attempt: number;
        query: string;
        result_count: number;
        quality_score: number;
        threshold: number;
        accepted: boolean;
    }[];

    trace: {
        step: string;
        status: string;
        detail: Record<string, unknown>;
    }[];

    decision: "accepted" | "best_effort";
    quality_score: number;

    filters: {
        collection_ids: string[];
    };

    count: number;

    results: {
        rank: number;
        keyframe_id: string;
        collection_id: string;
        video_id: string;
        frame_number: number;
        frame_id: number;
        timestamp_ms: number;
        image_path: string;
        video_path: string;
        image_url: string;
        video_url: string;
        score: number;
        domains?: string[];
        routed_domains?: string[];
        matched_objects?: string[];

        score_components?: {
            clip: number;
            object_bow: number;
            domain: number;
        };
    }[];
}
