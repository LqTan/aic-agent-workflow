import { VdieoSearchResponse, VideoSearchRequest } from "../../domain/models/video-search.model";

export interface VideoSearchService {
    search(
        request: VideoSearchRequest,
    ): Promise<VdieoSearchResponse>;
}
