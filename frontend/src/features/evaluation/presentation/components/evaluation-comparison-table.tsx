import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { EvaluationRun } from "../../domain/models/evaluation.model";

interface EvaluationComparisonTableProps {
    runs: EvaluationRun[];
}

const formatTimestamp = (iso: string): string => {
    const date = new Date(iso);
    return date.toLocaleString("en-US", {
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
};

export function EvaluationComparisonTable({
    runs,
}: EvaluationComparisonTableProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Per-run comparison</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[820px] text-left text-sm">
                        <thead className="text-xs uppercase tracking-wide text-muted-foreground">
                            <tr className="border-b">
                                <th className="px-3 py-2 font-medium">Goal</th>
                                <th className="px-3 py-2 font-medium">Decision</th>
                                <th className="px-3 py-2 font-medium">Quality</th>
                                <th className="px-3 py-2 font-medium">Threshold</th>
                                <th className="px-3 py-2 font-medium">Δ</th>
                                <th className="px-3 py-2 font-medium">Attempts</th>
                                <th className="px-3 py-2 font-medium">Latency</th>
                                <th className="px-3 py-2 font-medium">When</th>
                                <th className="px-3 py-2 font-medium text-right">
                                    Inspect
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {runs.map((run) => {
                                const delta =
                                    run.qualityScore - run.threshold;

                                return (
                                    <tr
                                        key={run.id}
                                        className="transition hover:bg-muted/30"
                                    >
                                        <td className="max-w-[320px] truncate px-3 py-3 font-medium">
                                            {run.goal}
                                        </td>
                                        <td className="px-3 py-3">
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
                                        </td>
                                        <td className="px-3 py-3 tabular-nums">
                                            {(run.qualityScore * 100).toFixed(1)}%
                                        </td>
                                        <td className="px-3 py-3 tabular-nums text-muted-foreground">
                                            {(run.threshold * 100).toFixed(0)}%
                                        </td>
                                        <td
                                            className={`px-3 py-3 tabular-nums ${
                                                delta >= 0
                                                    ? "text-emerald-600"
                                                    : "text-destructive"
                                            }`}
                                        >
                                            {delta >= 0 ? "+" : ""}
                                            {(delta * 100).toFixed(1)}%
                                        </td>
                                        <td className="px-3 py-3 tabular-nums">
                                            {run.attempts}
                                        </td>
                                        <td className="px-3 py-3 tabular-nums">
                                            {(run.latencyMs / 1000).toFixed(2)}s
                                        </td>
                                        <td className="px-3 py-3 text-xs text-muted-foreground">
                                            {formatTimestamp(run.timestamp)}
                                        </td>
                                        <td className="px-3 py-3 text-right">
                                            <Link
                                                href={`/analysis/${run.id}`}
                                                className="text-xs font-semibold text-primary hover:underline"
                                            >
                                                Open →
                                            </Link>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
}
