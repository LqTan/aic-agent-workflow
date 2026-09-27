"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { VideoSearchResponse } from "../../domain/models/video-search.model";
import { VideoSearchResultCard } from "./video-search-result-card";

interface VideoSearchResultsProps {
    data: VideoSearchResponse;
}

export function VideoSearchResults({
    data,
}: VideoSearchResultsProps) {
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
                    /* autoplay blocked by browser; user can press play */
                });
            }
        }
    }, [active]);

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
                    Tìm thấy {data.count} kết quả — bấm vào card để xem video
                </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {data.results.map((result) => (
                    <VideoSearchResultCard
                        key={result.keyframeId}
                        result={result}
                        onSelect={(videoUrl, timestampMs) =>
                            setActive({ url: videoUrl, seekMs: timestampMs })
                        }
                    />
                ))}
            </div>

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
        </section>
    );
}