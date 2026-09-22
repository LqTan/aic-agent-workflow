"use client";

import { useEvaluationOverview } from "../hooks/use-evaluation";
import { EvaluationComparisonTable } from "./evaluation-comparison-table";
import { EvaluationOverviewView } from "./evaluation-overview-view";

function EvaluationSkeleton() {
    return (
        <div className="space-y-4">
            <div className="h-32 animate-pulse rounded-xl bg-muted" />
            <div className="grid gap-4 lg:grid-cols-2">
                <div className="h-48 animate-pulse rounded-xl bg-muted" />
                <div className="h-48 animate-pulse rounded-xl bg-muted" />
            </div>
            <div className="h-72 animate-pulse rounded-xl bg-muted" />
        </div>
    );
}

function EvaluationError({ error }: { error: Error }) {
    return (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-6">
            <p className="text-sm font-semibold text-destructive">
                Failed to load evaluation
            </p>
            <p className="mt-1 text-sm text-destructive/80">{error.message}</p>
        </div>
    );
}

export function EvaluationPage() {
    const { data, isLoading, error } = useEvaluationOverview();

    if (isLoading || !data) {
        return <EvaluationSkeleton />;
    }

    if (error) {
        return <EvaluationError error={error} />;
    }

    return (
        <div className="space-y-6">
            <EvaluationOverviewView overview={data} />
            <EvaluationComparisonTable runs={data.runs} />
        </div>
    );
}
