"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AgentTrace } from "@/features/video-search/presentation/components/agent-trace";
import { VideoSearchResults } from "@/features/video-search/presentation/components/video-search-results";
import type { AnalysisDetail } from "../../domain/models/analysis.model";

interface AnalysisDetailViewProps {
    runId: string;
    data: AnalysisDetail;
}

export function AnalysisDetailView({ runId, data }: AnalysisDetailViewProps) {
    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Run {runId}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                    <div className="grid gap-3 md:grid-cols-2">
                        <div>
                            <p className="font-medium">Goal</p>
                            <p className="text-muted-foreground">{data.goal}</p>
                        </div>
                        <div>
                            <p className="font-medium">Final decision</p>
                            <p className="text-muted-foreground">
                                {data.decision === "accepted"
                                    ? "Đạt ngưỡng"
                                    : "Best effort"}
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
                    </div>
                </CardContent>
            </Card>

            <AgentTrace data={data} />

            <VideoSearchResults data={data} />
        </div>
    );
}
