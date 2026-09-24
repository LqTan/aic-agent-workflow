"use client";
import { useMemo, useState } from "react";
import { VideoSearchResponse, VideoSearchRequest } from "../../domain/models/video-search.model";
import { HttpVideoSearchService } from "../../infrastructure/services/video-search.service";
import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { SearchVideoUseCase } from "../../application/use-cases/search-videos.use-case";

export function useVideoSearch() {
    const [data, setData] = useState<VideoSearchResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    // Always use the real HttpVideoSearchService backed by the bundled
    // FastAPI server. Mock data has been removed from the MVP.
    const useCase = useMemo(
        () =>
            new SearchVideoUseCase(
                new HttpVideoSearchService(new FetchApiClient()),
            ),
        [],
    );

    const search = async (
        request: VideoSearchRequest,
    ): Promise<void> => {
        try {
            setIsLoading(true);
            setError(null);
            setData(null);
            const result = await useCase.execute(request);

            setData(result);
        } catch (error) {
            setError(
                error instanceof Error ? error : new Error("Unexpected error"),
            );
        } finally {
            setIsLoading(false);
        }
    };

    const reset = (): void => {
        setData(null);
        setError(null);
    };
    return { data, isLoading, error, search, reset };
}
