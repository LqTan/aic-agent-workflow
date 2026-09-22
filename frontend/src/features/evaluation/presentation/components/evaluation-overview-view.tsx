import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { EvaluationOverview } from "../../domain/models/evaluation.model";

interface EvaluationOverviewViewProps {
    overview: EvaluationOverview;
}

export function EvaluationOverviewView({
    overview,
}: EvaluationOverviewViewProps) {
    const acceptanceRate = overview.totalRuns
        ? Math.round(
              (overview.decisionDistribution.accepted / overview.totalRuns) *
                  100,
          )
        : 0;

    const maxBucket = Math.max(
        ...overview.qualityDistribution.map((bucket) => bucket.count),
        1,
    );

    const summaryItems: Array<{ label: string; value: string }> = [
        {
            label: "Total runs",
            value: overview.totalRuns.toString(),
        },
        {
            label: "Avg. quality",
            value: `${(overview.averageQuality * 100).toFixed(1)}%`,
        },
        {
            label: "Acceptance rate",
            value: `${acceptanceRate}%`,
        },
        {
            label: "Avg. attempts",
            value: overview.averageAttempts.toFixed(2),
        },
        {
            label: "Avg. latency",
            value: `${(overview.averageLatency / 1000).toFixed(2)}s`,
        },
        {
            label: "Default threshold",
            value: `${(overview.thresholdDefault * 100).toFixed(0)}%`,
        },
    ];

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Retrieval evaluation</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        {summaryItems.map((item) => (
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
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            <div className="grid gap-4 lg:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Quality distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {overview.qualityDistribution.map((bucket) => {
                                const widthPct = Math.max(
                                    2,
                                    (bucket.count / maxBucket) * 100,
                                );

                                return (
                                    <div
                                        key={bucket.bucket}
                                        className="space-y-1"
                                    >
                                        <div className="flex items-center justify-between text-xs">
                                            <span className="font-medium">
                                                {bucket.bucket}
                                            </span>
                                            <span className="tabular-nums text-muted-foreground">
                                                {bucket.count} runs
                                            </span>
                                        </div>
                                        <div className="h-2 overflow-hidden rounded-full bg-muted">
                                            <div
                                                className="h-full bg-primary transition-all"
                                                style={{
                                                    width: `${widthPct}%`,
                                                }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Decision split</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <DecisionBar
                                label="Accepted"
                                count={overview.decisionDistribution.accepted}
                                total={overview.totalRuns}
                                variant="default"
                            />
                            <DecisionBar
                                label="Best effort"
                                count={
                                    overview.decisionDistribution.bestEffort
                                }
                                total={overview.totalRuns}
                                variant="secondary"
                            />
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

interface DecisionBarProps {
    label: string;
    count: number;
    total: number;
    variant: "default" | "secondary";
}

function DecisionBar({ label, count, total, variant }: DecisionBarProps) {
    const widthPct = total ? Math.max(2, (count / total) * 100) : 2;
    const color = variant === "default" ? "bg-primary" : "bg-muted-foreground";

    return (
        <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
                <span className="font-medium">{label}</span>
                <span className="tabular-nums text-muted-foreground">
                    {count} · {total ? Math.round((count / total) * 100) : 0}%
                </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-muted">
                <div
                    className={`h-full ${color} transition-all`}
                    style={{ width: `${widthPct}%` }}
                />
            </div>
        </div>
    );
}
