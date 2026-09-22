import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import type { HistoryEntry } from "../../domain/models/history.model";

interface HistoryTableProps {
    entries: HistoryEntry[];
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

export function HistoryTable({ entries }: HistoryTableProps) {
    if (entries.length === 0) {
        return (
            <div className="rounded-lg border border-dashed p-12 text-center">
                <p className="text-sm text-muted-foreground">
                    Không có truy vấn nào khớp bộ lọc hiện tại.
                </p>
            </div>
        );
    }

    return (
        <div className="overflow-hidden rounded-xl border bg-card">
            <div className="overflow-x-auto">
                <table className="w-full min-w-[820px] text-left text-sm">
                    <thead className="bg-muted/40 text-xs uppercase tracking-wide text-muted-foreground">
                        <tr>
                            <th className="px-4 py-3 font-medium">Goal</th>
                            <th className="px-4 py-3 font-medium">Decision</th>
                            <th className="px-4 py-3 font-medium">Quality</th>
                            <th className="px-4 py-3 font-medium">Attempts</th>
                            <th className="px-4 py-3 font-medium">Results</th>
                            <th className="px-4 py-3 font-medium">Latency</th>
                            <th className="px-4 py-3 font-medium">Collections</th>
                            <th className="px-4 py-3 font-medium">Timestamp</th>
                            <th className="px-4 py-3 font-medium text-right">
                                Detail
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {entries.map((entry) => (
                            <tr
                                key={entry.id}
                                className="transition hover:bg-muted/30"
                            >
                                <td className="max-w-[360px] truncate px-4 py-3 font-medium">
                                    {entry.goal}
                                </td>
                                <td className="px-4 py-3">
                                    <Badge
                                        variant={
                                            entry.decision === "accepted"
                                                ? "default"
                                                : "secondary"
                                        }
                                    >
                                        {entry.decision === "accepted"
                                            ? "Accepted"
                                            : "Best effort"}
                                    </Badge>
                                </td>
                                <td className="px-4 py-3 tabular-nums">
                                    {(entry.qualityScore * 100).toFixed(1)}%
                                </td>
                                <td className="px-4 py-3 tabular-nums">
                                    {entry.attempts}
                                </td>
                                <td className="px-4 py-3 tabular-nums">
                                    {entry.resultCount}
                                </td>
                                <td className="px-4 py-3 tabular-nums">
                                    {(entry.durationMs / 1000).toFixed(2)}s
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex flex-wrap gap-1">
                                        {entry.collectionIds.map((id) => (
                                            <Badge
                                                key={id}
                                                variant="outline"
                                                className="font-mono text-[10px]"
                                            >
                                                {id}
                                            </Badge>
                                        ))}
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-xs text-muted-foreground">
                                    {formatTimestamp(entry.timestamp)}
                                </td>
                                <td className="px-4 py-3 text-right">
                                    <Link
                                        href={`/analysis/${entry.id}`}
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
        </div>
    );
}
