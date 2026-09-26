import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentSearchResponse } from "../../domain/models/agent-search.model";

interface AgentTraceProps {
    data: AgentSearchResponse;
}

export function AgentTrace({ data }: AgentTraceProps) {
    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between gap-4">
                    <CardTitle>Agent Workflow (n8n)</CardTitle>
                    <div className="flex items-center gap-2">
                        <Badge
                            variant={
                                data.decision === "accepted"
                                    ? "default"
                                    : "secondary"
                            }
                        >
                            {data.decision}
                        </Badge>
                        <Badge variant="outline">{data.planner}</Badge>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="space-y-6">
                <div className="grid gap-3 text-sm md:grid-cols-2">
                    <div>
                        <p className="font-medium">Run ID</p>
                        <p className="font-mono text-xs text-muted-foreground">
                            {data.id ?? "(no id returned)"}
                        </p>
                    </div>
                    <div>
                        <p className="font-medium">Intent</p>
                        <p className="text-muted-foreground">
                            {data.plan.intent}
                        </p>
                    </div>
                    <div>
                        <p className="font-medium">Search query</p>
                        <p className="text-muted-foreground">
                            {data.plan.searchQuery}
                        </p>
                    </div>
                    <div>
                        <p className="font-medium">Final quality</p>
                        <p className="text-muted-foreground">
                            {(data.qualityScore * 100).toFixed(1)}%
                        </p>
                    </div>
                    <div>
                        <p className="font-medium">Attempts</p>
                        <p className="text-muted-foreground">
                            {data.attempts.length}
                        </p>
                    </div>
                    <div>
                        <p className="font-medium">Duration</p>
                        <p className="text-muted-foreground">
                            {(data.durationMs / 1000).toFixed(2)}s
                        </p>
                    </div>
                </div>

                {data.plan.objects.length > 0 && (
                    <div className="space-y-2">
                        <p className="text-sm font-medium">Objects</p>
                        <div className="flex flex-wrap gap-2">
                            {data.plan.objects.map((object) => (
                                <Badge key={object} variant="outline">
                                    {object}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}

                {data.attempts.length > 0 && (
                    <div className="space-y-3">
                        <p className="text-sm font-medium">Attempts</p>
                        {data.attempts.map((attempt) => (
                            <div
                                key={attempt.attempt}
                                className="rounded-lg border p-3 text-sm"
                            >
                                <div className="flex items-center justify-between gap-4">
                                    <span>Attempt {attempt.attempt}</span>
                                    <Badge
                                        variant={
                                            attempt.accepted
                                                ? "default"
                                                : "secondary"
                                        }
                                    >
                                        {attempt.accepted ? "Accepted" : "Retry"}
                                    </Badge>
                                </div>
                                <p className="mt-2 text-muted-foreground">
                                    {attempt.query}
                                </p>
                                <p className="mt-1 text-xs text-muted-foreground">
                                    Quality:{" "}
                                    {(attempt.qualityScore * 100).toFixed(1)}%
                                </p>
                            </div>
                        ))}
                    </div>
                )}

                {data.trace.length > 0 && (
                    <div className="space-y-3">
                        <p className="text-sm font-medium">Execution trace</p>
                        <div className="space-y-2">
                            {data.trace.map((item, index) => (
                                <div
                                    key={`${item.step}-${index}`}
                                    className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
                                >
                                    <span>{item.step}</span>
                                    <Badge variant="outline">
                                        {item.status}
                                    </Badge>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}