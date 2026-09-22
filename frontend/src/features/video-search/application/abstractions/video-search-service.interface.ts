import { VideoSearchRequest, VideoSearchResponse } from "../../domain/models/video-search.model";

export interface VideoSearchService {
    search(
        request: VideoSearchRequest,
    ): Promise<VideoSearchResponse>;
}
