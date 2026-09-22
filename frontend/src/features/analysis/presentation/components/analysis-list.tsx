import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { AnalysisRunSummary } from "../../domain/models/analysis.model";

interface AnalysisListProps {
    runs: AnalysisRunSummary[];
}

const formatTimestamp = (iso: string): string => {
    const date = new Date(iso);
    return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
};

export function AnalysisList({ runs }: AnalysisListProps) {
    if (runs.length === 0) {
        return (
            <div className="rounded-lg border border-dashed p-12 text-center">
                <p className="text-sm text-muted-foreground">
                    Chưa có run nào để phân tích.
                </p>
            </div>
        );
    }

    return (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {runs.map((run) => (
                <Card key={run.id} className="flex flex-col">
                    <CardHeader>
                        <div className="flex items-center justify-between gap-3">
                            <CardTitle className="line-clamp-2 text-base">
                                {run.goal}
                            </CardTitle>
                            <Badge
                                variant={
                                    run.decision === "accepted"
                                        ? "default"
                                        : "secondary"
                                }
                            >
                                {run.decision === "accepted"
                                    ? "Accepted"
                                    : "Best effort"}
                            </Badge>
                        </div>
                    </CardHeader>

                    <CardContent className="flex flex-1 flex-col gap-4 text-sm">
                        <div className="grid grid-cols-2 gap-2 text-muted-foreground">
                            <span>Quality</span>
                            <span className="tabular-nums text-foreground">
                                {(run.qualityScore * 100).toFixed(1)}%
                            </span>

                            <span>Attempts</span>
                            <span className="tabular-nums text-foreground">
                                {run.attempts}
                            </span>

                            <span>Results</span>
                            <span className="tabular-nums text-foreground">
                                {run.resultCount}
                            </span>

                            <span>Latency</span>
                            <span className="tabular-nums text-foreground">
                                {(run.durationMs / 1000).toFixed(2)}s
                            </span>

                            <span>Planner</span>
                            <span className="text-foreground">{run.planner}</span>
                        </div>

                        <div className="flex flex-wrap gap-1">
                            {run.collectionIds.map((id) => (
                                <Badge
                                    key={id}
                                    variant="outline"
                                    className="font-mono text-[10px]"
                                >
                                    {id}
                                </Badge>
                            ))}
                        </div>

                        <div className="mt-auto flex items-center justify-between gap-3 border-t pt-3 text-xs">
                            <span className="text-muted-foreground">
                                {formatTimestamp(run.timestamp)}
                            </span>
                            <Link
                                href={`/analysis/${run.id}`}
                                className="font-semibold text-primary hover:underline"
                            >
                                Open run →
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
