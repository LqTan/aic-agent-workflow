"use client";

import { useAnalysisList } from "../hooks/use-analysis-list";
import { AnalysisCharts } from "./analysis-charts";
import { AnalysisList as AnalysisListView } from "./analysis-list";

function ListSkeleton() {
    return (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
                <div
                    key={index}
                    className="h-56 animate-pulse rounded-xl bg-muted"
                />
            ))}
        </div>
    );
}

function ListError({ error }: { error: Error }) {
    return (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-6">
            <p className="text-sm font-semibold text-destructive">
                Failed to load runs
            </p>
            <p className="mt-1 text-sm text-destructive/80">{error.message}</p>
        </div>
    );
}

export function AnalysisListPage() {
    const { data, isLoading, error } = useAnalysisList();

    if (isLoading) {
        return <ListSkeleton />;
    }

    if (error) {
        return <ListError error={error} />;
    }

    if (!data) {
        return <ListSkeleton />;
    }

    return (
        <div className="space-y-6">
            <AnalysisCharts runs={data.runs} />
            <AnalysisListView runs={data.runs} />
        </div>
    );
}
