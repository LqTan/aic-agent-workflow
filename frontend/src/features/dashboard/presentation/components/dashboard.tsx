"use client";

import { DashboardOverview } from "../../domain/models/dashboard.model";
import { useDashboardOverview } from "../hooks/use-dashboard";
import { DashboardQualityTrend } from "./dashboard-quality-trend";
import { DashboardRecentRuns } from "./dashboard-recent-runs";
import { DashboardStats } from "./dashboard-stats";

function DashboardSkeleton() {
    return (
        <div className="space-y-6">
            <div className="h-32 animate-pulse rounded-xl bg-muted" />
            <div className="grid gap-4 lg:grid-cols-3">
                <div className="h-40 animate-pulse rounded-xl bg-muted lg:col-span-2" />
                <div className="h-40 animate-pulse rounded-xl bg-muted" />
            </div>
            <div className="h-72 animate-pulse rounded-xl bg-muted" />
        </div>
    );
}

function DashboardError({ error }: { error: Error }) {
    return (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-6">
            <p className="text-sm font-semibold text-destructive">
                Failed to load dashboard
            </p>
            <p className="mt-1 text-sm text-destructive/80">{error.message}</p>
        </div>
    );
}

export function Dashboard() {
    const { data, isLoading, error } = useDashboardOverview();

    if (isLoading) {
        return <DashboardSkeleton />;
    }

    if (error) {
        return <DashboardError error={error} />;
    }

    if (!data) {
        return <DashboardSkeleton />;
    }

    return (
        <div className="space-y-6">
            <DashboardStats overview={data} />
            <div className="grid gap-4 lg:grid-cols-3">
                <div className="lg:col-span-2">
                    <DashboardRecentRuns runs={data.recentRuns} />
                </div>
                <DashboardQualityTrend points={data.qualityTrend} />
            </div>
        </div>
    );
}

export type { DashboardOverview };
