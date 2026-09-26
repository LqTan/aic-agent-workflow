import { ApiClient } from "@/lib/api/abstractions/api-client.interface";
import { VideoSearchService } from "../../application/abstractions/video-search-service.interface";
import { VideoSearchRequest, VideoSearchResponse } from "../../domain/models/video-search.model";
import { LocalSearchResponseDto } from "../dtos/local-search.dto";
import { VideoSearchMapper } from "../mappers/video-search.mapper";

export class HttpVideoSearchService implements VideoSearchService {
    constructor(
        private readonly apiClient: ApiClient,
    ) {}

    async search(request: VideoSearchRequest): Promise<VideoSearchResponse> {
        const response = await this.apiClient.request<LocalSearchResponseDto>(
            "/kis/search/",
            {
                method: "POST",
                body: JSON.stringify({
                    query: request.query,
                    top_k: request.topK ?? 12,
                }),
            },
        );

        return VideoSearchMapper.fromLocalSearch(response);
    }
}
