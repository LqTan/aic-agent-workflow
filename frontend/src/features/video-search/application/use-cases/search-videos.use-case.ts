import { VdieoSearchResponse, VideoSearchRequest } from "../../domain/models/video-search.model";
import { VideoSearchService } from "../abstractions/video-search-service.interface";

export class SearchVideoUseCase {
    constructor(
        private readonly videoSearchService: VideoSearchService,
    ) {}

    async execute(
        request: VideoSearchRequest,
    ): Promise<VdieoSearchResponse> {
        const query = request.query.trim();

        if (!query) {
            throw new Error("Search query is required.");
        }

        return this.videoSearchService.search({
            ...request,
            query,
        });
    }
}
