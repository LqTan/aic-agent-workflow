import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardOverview } from "../../domain/models/dashboard.model";

interface DashboardStatsProps {
    overview: DashboardOverview;
}

interface StatItem {
    label: string;
    value: string;
    description: string;
}

export function DashboardStats({ overview }: DashboardStatsProps) {
    const acceptedRate = overview.totalQueries
        ? Math.round((overview.acceptedQueries / overview.totalQueries) * 100)
        : 0;

    const items: StatItem[] = [
        {
            label: "Total queries",
            value: overview.totalQueries.toLocaleString("en-US"),
            description: `${overview.acceptedQueries} accepted · ${overview.bestEffortQueries} best-effort`,
        },
        {
            label: "Acceptance rate",
            value: `${acceptedRate}%`,
            description: "Above quality threshold",
        },
        {
            label: "Avg. quality score",
            value: `${(overview.averageQualityScore * 100).toFixed(1)}%`,
            description: "Across all runs",
        },
        {
            label: "Avg. attempts",
            value: overview.averageAttempts.toFixed(2),
            description: "Refinements per query",
        },
        {
            label: "Indexed videos",
            value: overview.totalIndexedVideos.toLocaleString("en-US"),
            description: `${overview.totalCollections} collections`,
        },
        {
            label: "Avg. latency",
            value: `${(overview.averageDurationMs / 1000).toFixed(2)}s`,
            description: "End-to-end agent run",
        },
    ];

    return (
        <Card>
            <CardHeader>
                <CardTitle>System overview</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {items.map((item) => (
                        <div
                            key={item.label}
                            className="rounded-lg border bg-muted/40 p-4"
                        >
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">
                                {item.label}
                            </p>
                            <p className="mt-2 text-2xl font-semibold tabular-nums">
                                {item.value}
                            </p>
                            <p className="mt-1 text-xs text-muted-foreground">
                                {item.description}
                            </p>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
