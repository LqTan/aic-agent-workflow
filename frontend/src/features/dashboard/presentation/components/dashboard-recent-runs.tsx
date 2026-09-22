import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { SearchRunSummary } from "../../domain/models/dashboard.model";

interface DashboardRecentRunsProps {
    runs: SearchRunSummary[];
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

export function DashboardRecentRuns({ runs }: DashboardRecentRunsProps) {
    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between gap-4">
                    <CardTitle>Recent runs</CardTitle>
                    <Link
                        href="/history"
                        className="text-xs font-medium text-primary hover:underline"
                    >
                        View all
                    </Link>
                </div>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[640px] text-left text-sm">
                        <thead className="text-xs uppercase tracking-wide text-muted-foreground">
                            <tr className="border-b">
                                <th className="px-3 py-2 font-medium">Goal</th>
                                <th className="px-3 py-2 font-medium">Decision</th>
                                <th className="px-3 py-2 font-medium">Quality</th>
                                <th className="px-3 py-2 font-medium">Results</th>
                                <th className="px-3 py-2 font-medium">When</th>
                                <th className="px-3 py-2 font-medium text-right">
                                    Detail
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {runs.map((run) => (
                                <tr
                                    key={run.id}
                                    className="transition hover:bg-muted/40"
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
                                    <td className="px-3 py-3 tabular-nums">
                                        {run.resultCount}
                                    </td>
                                    <td className="px-3 py-3 text-xs text-muted-foreground">
                                        {formatTimestamp(run.timestamp)}
                                    </td>
                                    <td className="px-3 py-3 text-right">
                                        <Link
                                            href={`/analysis/${run.id}`}
                                            className="text-xs font-semibold text-primary hover:underline"
                                        >
                                            Inspect →
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
}
