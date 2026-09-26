import type { AgentSearchResponse } from "../../domain/models/agent-search.model";
import { AgentResultCard } from "./agent-result-card";

interface AgentSearchResultsProps {
    data: AgentSearchResponse;
}

export function AgentSearchResults({ data }: AgentSearchResultsProps) {
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
                <h2 className="text-xl font-semibold">Kết quả từ n8n</h2>
                <p className="text-sm text-muted-foreground">
                    Tìm thấy {data.resultCount} keyframe trong{" "}
                    {(data.durationMs / 1000).toFixed(2)}s
                </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {data.results.map((result) => (
                    <AgentResultCard
                        key={result.keyframeId}
                        result={result}
                    />
                ))}
            </div>
        </section>
    );
}