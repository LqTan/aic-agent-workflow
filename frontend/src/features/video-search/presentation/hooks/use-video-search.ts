"use client";
import { useState } from "react";
import { VideoSearchResponse, VideoSearchRequest } from "../../domain/models/video-search.model";
import { searchVideoUseCase } from "../../dependency-injection";

export function useVideoSearch() {
    const [data, setData] = useState<VideoSearchResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const search = async (
        request: VideoSearchRequest,
    ): Promise<void> => {
        try {
            setIsLoading(true);
            setError(null);
            setData(null);
            const result = await searchVideoUseCase.execute(request);

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
