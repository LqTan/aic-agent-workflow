import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VideoSearchResponse } from "../../domain/models/video-search.model";

interface AgentTraceProps {
    data: VideoSearchResponse;
}

export function AgentTrace({
    data,
}: AgentTraceProps) {
    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between gap-4">
                    <CardTitle>Agent Workflow</CardTitle>

                    <Badge
                        variant={
                            data.decision === "accepted"
                                ? "default"
                                : "secondary"
                        }
                    >
                        {data.decision}
                    </Badge>
                </div>
            </CardHeader>

            <CardContent className="space-y-6">
                <div className="grid gap-3 text-sm md:grid-cols-2">
                    <div>
                        <p className="font-medium">
                            Intent
                        </p>

                        <p className="text-muted-foreground">
                            {data.plan.intent}
                        </p>
                    </div>

                    <div>
                        <p className="font-medium">
                            Planner
                        </p>

                        <p className="text-muted-foreground">
                            {data.plan.planner}
                        </p>
                    </div>

                    <div>
                        <p className="font-medium">
                            Search query
                        </p>

                        <p className="text-muted-foreground">
                            {data.plan.searchQuery}
                        </p>
                    </div>

                    <div>
                        <p className="font-medium">
                            Quality score
                        </p>

                        <p className="text-muted-foreground">
                            {(data.qualityScore * 100).toFixed(1)}%
                        </p>
                    </div>
                </div>

                {data.plan.objects.length > 0 && (
                    <div className="space-y-2">
                        <p className="text-sm font-medium">
                            Objects
                        </p>

                        <div className="flex flex-wrap gap-2">
                            {data.plan.objects.map((object) => (
                                <Badge
                                    key={object}
                                    variant="outline"
                                >
                                    {object}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}

                {data.plan.actions.length > 0 && (
                    <div className="space-y-2">
                        <p className="text-sm font-medium">
                            Actions
                        </p>

                        <div className="flex flex-wrap gap-2">
                            {data.plan.actions.map((action) => (
                                <Badge
                                    key={action}
                                    variant="secondary"
                                >
                                    {action}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}

                {data.attempts.length > 0 && (
                    <div className="space-y-3">
                        <p className="text-sm font-medium">
                            Search attempts
                        </p>

                        {data.attempts.map((attempt) => (
                            <div
                                key={attempt.attempt}
                                className="rounded-lg border p-3 text-sm"
                            >
                                <div className="flex items-center justify-between gap-4">
                                    <span>
                                        Attempt {attempt.attempt}
                                    </span>

                                    <Badge
                                        variant={
                                            attempt.accepted
                                                ? "default"
                                                : "secondary"
                                        }
                                    >
                                        {attempt.accepted
                                            ? "Accepted"
                                            : "Retry"}
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
                        <p className="text-sm font-medium">
                            Execution trace
                        </p>

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
    )
}
