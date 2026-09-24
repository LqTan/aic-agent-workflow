"use client"

import { useVideoSearch } from "../hooks/use-video-search"
import { AgentTrace } from "./agent-trace";
import { VideoSearchForm } from "./video-search-form";
import { VideoSearchResults } from "./video-search-results";

export function VideoSearch() {
    const { data, isLoading, error, search } = useVideoSearch();
    const handleSearch = async (
        query: string,
    ): Promise<void> => {
        await search({
            query,
            topK: 12,
            qualityThreshold: 0.42,
            maxAttempts: 2,
        });
    };

    return (
        <div className="space-y-8">
            <section className="space-y-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Video Search Agent
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        Tìm kiếm nội dung video bằng mô tả ngôn ngữ tự nhiên.
                    </p>
                </div>

                <VideoSearchForm
                    isLoading={isLoading}
                    onSearch={handleSearch}
                />

                {error && (
                    <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
                        <p className="text-sm text-destructive">
                            {error.message}
                        </p>
                    </div>
                )}
            </section>

            {data && (
                <>
                    <AgentTrace data={data} />
                    <VideoSearchResults data={data} />
                </>
            )}
        </div>
    );
}
