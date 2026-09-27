"use client";

import { useEffect, useRef, useState } from "react";
import { useAgentSearch } from "../hooks/use-agent-search";
import { AgentSearchForm } from "./agent-search-form";
import { AgentSearchResults } from "./agent-search-results";
import { AgentTrace } from "./agent-trace";
import { Button } from "@/components/ui/button";

export function AgentSearch() {
    const { data, isLoading, error, search, lastDurationMs } = useAgentSearch();
    const [active, setActive] = useState<{ url: string; seekMs: number } | null>(
        null,
    );
    const dialogRef = useRef<HTMLDialogElement | null>(null);
    const videoRef = useRef<HTMLVideoElement | null>(null);

    useEffect(() => {
        const dialog = dialogRef.current;
        if (!dialog) return;
        if (active && !dialog.open) {
            dialog.showModal();
        } else if (!active && dialog.open) {
            dialog.close();
        }
    }, [active]);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;
        if (active) {
            video.currentTime = active.seekMs / 1000;
            const playPromise = video.play();
            if (playPromise && typeof playPromise.catch === "function") {
                playPromise.catch(() => {
                    /* autoplay blocked */
                });
            }
        }
    }, [active]);

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
                    <AgentSearchResults
                        data={data}
                        onSelectVideo={(videoUrl, timestampMs) =>
                            setActive({ url: videoUrl, seekMs: timestampMs })
                        }
                    />
                </>
            )}

            <dialog
                ref={dialogRef}
                className="fixed top-1/2 left-1/2 max-h-[90vh] max-w-3xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border bg-background p-4 shadow-2xl backdrop:bg-black/60"
                onClose={() => setActive(null)}
                onClick={(event) => {
                    if (event.target === dialogRef.current) {
                        setActive(null);
                    }
                }}
            >
                {active && (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between gap-4">
                            <h3 className="text-sm font-semibold">
                                Phát từ keyframe (seek{" "}
                                {Math.round(active.seekMs / 1000)}s)
                            </h3>
                            <Button
                                type="button"
                                size="sm"
                                variant="outline"
                                onClick={() => setActive(null)}
                            >
                                Đóng
                            </Button>
                        </div>
                        <video
                            ref={videoRef}
                            src={active.url}
                            controls
                            className="w-full rounded-lg bg-black"
                        />
                    </div>
                )}
            </dialog>
        </div>
    );
}