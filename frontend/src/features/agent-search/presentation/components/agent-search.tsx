"use client";

import { useAgentSearch } from "../hooks/use-agent-search";
import { AgentSearchForm } from "./agent-search-form";
import { AgentSearchResults } from "./agent-search-results";
import { AgentTrace } from "./agent-trace";

export function AgentSearch() {
    const { data, isLoading, error, search, lastDurationMs } = useAgentSearch();

    const handleSearch = async (query: string, topK: number) => {
        await search({ query, topK, maxAttempts: 2 });
    };

    return (
        <div className="space-y-8">
            <section className="space-y-4">
                <div className="rounded-lg border border-dashed bg-muted/30 p-4 text-sm text-muted-foreground">
                    Endpoint:{" "}
                    <code className="font-mono text-xs">
                        POST http://localhost:5678/webhook/aic-agent-search
                    </code>
                    <span className="ml-3 text-xs">
                        (qua n8n — mất 3–10s vì gọi LLM MiniMax)
                    </span>
                </div>

                <AgentSearchForm
                    isLoading={isLoading}
                    onSearch={handleSearch}
                />

                {isLoading && (
                    <div
                        data-testid="agent-loading"
                        className="flex items-center gap-3 rounded-lg border border-primary/30 bg-primary/5 p-4"
                    >
                        <span className="inline-block size-3 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                        <span className="text-sm">
                            Đang chạy workflow n8n (Planner → Retrieval →
                            Validation → Persist)…
                        </span>
                    </div>
                )}

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
                    {lastDurationMs !== null && (
                        <div className="rounded-md border bg-card px-4 py-2 text-xs text-muted-foreground">
                            Response từ n8n trong {lastDurationMs}ms
                            (đã qua 8 node: Webhook → Planner → Retrieval →
                            Validation → Persist → Finalize → Respond).
                        </div>
                    )}
                    <AgentTrace data={data} />
                    <AgentSearchResults data={data} />
                </>
            )}
        </div>
    );
}