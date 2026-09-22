import { VideoSearchService } from "../../../application/abstractions/video-search-service.interface";
import { VideoSearchRequest, VideoSearchResponse } from "../../../domain/models/video-search.model";
import {
    alternativeSearchResponses,
    baseSearchResponse,
} from "../fixtures/video-search.fixtures";

const wait = (ms: number): Promise<void> =>
    new Promise((resolve) => setTimeout(resolve, ms));

export class MockVideoSearchService implements VideoSearchService {
    private callCount = 0;

    async search(request: VideoSearchRequest): Promise<VideoSearchResponse> {
        await wait(450);

        const response =
            this.callCount % 3 === 0
                ? baseSearchResponse
                : alternativeSearchResponses[
                      this.callCount % alternativeSearchResponses.length
                  ];

        this.callCount += 1;

        const goal = request.query?.trim() || response.goal;

        return {
            ...response,
            goal,
        };
    }
}
