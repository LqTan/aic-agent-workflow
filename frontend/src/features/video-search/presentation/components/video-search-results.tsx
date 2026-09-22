import { VideoSearchResponse } from "../../domain/models/video-search.model";
import { VideoSearchResultCard } from "./video-search-result-card";

interface VideoSearchResultsProps {
    data: VideoSearchResponse;
}

export function VideoSearchResults({
    data,
}: VideoSearchResultsProps) {
    if (data.results.length === 0) {
        return (
            <div className="rounded-lg border border-dashed p-8 text-center">
                <p className="text-sm text-muted-foreground">
                    Không tìm thấy kết quả phù hợp.
                </p>
            </div>
        );
    }

    return (
        <section className="space-y-4">
            <div>
                <h2 className="text-xl font-semibold">
                    Kết quả tìm kiếm
                </h2>

                <p className="text-sm text-muted-foreground">
                    Tìm thấy {data.count} kết quả
                </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {data.results.map((result) => (
                    <VideoSearchResultCard
                        key={result.keyframeId}
                        result={result}
                    />
                ))}
            </div>
        </section>
    );
}
