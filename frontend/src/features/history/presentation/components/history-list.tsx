"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useState } from "react";
import type {
    HistoryDecision,
    HistoryFilter,
} from "../../domain/models/history.model";
import { useHistory } from "../hooks/use-history";
import { HistoryTable } from "./history-table";

const DECISIONS: Array<{ value: HistoryDecision | "all"; label: string }> = [
    { value: "all", label: "Tất cả" },
    { value: "accepted", label: "Đạt ngưỡng" },
    { value: "best_effort", label: "Best effort" },
];

export function HistoryList() {
    const [decision, setDecision] = useState<HistoryDecision | "all">("all");
    const [query, setQuery] = useState("");

    const filter: HistoryFilter = {
        decision,
        query: query.trim() ? query.trim() : undefined,
    };

    const { data, isLoading, error } = useHistory(filter);

    return (
        <div className="space-y-4">
            <Card>
                <CardContent className="space-y-4 pt-6">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                        <div className="flex flex-wrap gap-2">
                            {DECISIONS.map((item) => (
                                <Button
                                    key={item.value}
                                    type="button"
                                    size="sm"
                                    variant={
                                        decision === item.value
                                            ? "default"
                                            : "outline"
                                    }
                                    onClick={() => setDecision(item.value)}
                                >
                                    {item.label}
                                </Button>
                            ))}
                        </div>

                        <div className="flex w-full items-center gap-2 md:w-auto">
                            <input
                                type="search"
                                value={query}
                                onChange={(event) => setQuery(event.target.value)}
                                placeholder="Tìm theo goal hoặc query..."
                                className="h-9 w-full min-w-[240px] rounded-md border bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:w-auto"
                            />
                        </div>
                    </div>

                    <div className="text-xs text-muted-foreground">
                        {isLoading
                            ? "Đang tải..."
                            : data
                              ? `${data.total} truy vấn khớp bộ lọc`
                              : ""}
                    </div>
                </CardContent>
            </Card>

            {error ? (
                <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-6">
                    <p className="text-sm font-semibold text-destructive">
                        Failed to load history
                    </p>
                    <p className="mt-1 text-sm text-destructive/80">
                        {error.message}
                    </p>
                </div>
            ) : (
                data && <HistoryTable entries={data.entries} />
            )}
        </div>
    );
}
