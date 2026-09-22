import { env } from "@/config/env";
import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { SearchVideoUseCase } from "./application/use-cases/search-videos.use-case";
import { HttpVideoSearchService } from "./infrastructure/services/video-search.service";
import { MockVideoSearchService } from "./infrastructure/mocks/services/mock-video-search.service";

const videoSearchService = env.useMocks
    ? new MockVideoSearchService()
    : new HttpVideoSearchService(new FetchApiClient());

export const searchVideoUseCase = new SearchVideoUseCase(videoSearchService);
