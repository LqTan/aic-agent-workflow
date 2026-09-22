import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { HttpVideoSearchService } from "./infrastructure/services/video-search.service";
import { SearchVideoUseCase } from "./application/use-cases/search-videos.use-case";

const apiClient = new FetchApiClient();

const videoSearchService = new HttpVideoSearchService(apiClient);

export const searchVideoUseCase = new SearchVideoUseCase(videoSearchService);
