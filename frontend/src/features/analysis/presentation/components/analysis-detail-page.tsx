"use client";

import { useAnalysisDetail } from "../hooks/use-analysis-detail";
import { AnalysisDetailView } from "./analysis-detail-view";

function DetailSkeleton() {
    return (
        <div className="space-y-4">
            <div className="h-32 animate-pulse rounded-xl bg-muted" />
            <div className="h-64 animate-pulse rounded-xl bg-muted" />
            <div className="h-96 animate-pulse rounded-xl bg-muted" />
        </div>
    );
}

function DetailError({ error }: { error: Error }) {
    return (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-6">
            <p className="text-sm font-semibold text-destructive">
                Failed to load run
            </p>
            <p className="mt-1 text-sm text-destructive/80">{error.message}</p>
        </div>
    );
}

export function AnalysisDetailPage({ runId }: { runId: string }) {
    const { data, isLoading, error } = useAnalysisDetail(runId);

    if (isLoading || !data) {
        return <DetailSkeleton />;
    }

    if (error) {
        return <DetailError error={error} />;
    }

    return <AnalysisDetailView runId={runId} data={data} />;
}
