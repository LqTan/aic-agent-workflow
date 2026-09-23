export interface LocalSearchRequestDto {
    query: string;
    top_k?: number;
}

export interface LocalSearchResponseDto {
    query: string;
    count: number;
    results: LocalSearchResultDto[];
}

export interface LocalSearchResultDto {
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
}
