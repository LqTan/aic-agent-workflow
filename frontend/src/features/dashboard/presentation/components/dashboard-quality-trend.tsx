import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { QualityTrendPoint } from "../../domain/models/dashboard.model";

interface DashboardQualityTrendProps {
    points: QualityTrendPoint[];
}

export function DashboardQualityTrend({ points }: DashboardQualityTrendProps) {
    const max = 1;
    const min = 0;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Quality trend (7 days)</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex h-40 items-end gap-3">
                    {points.map((point) => {
                        const heightPct = Math.max(
                            4,
                            ((point.averageQualityScore - min) / (max - min)) *
                                100,
                        );
                        return (
                            <div
                                key={point.date}
                                className="flex flex-1 flex-col items-center gap-2"
                            >
                                <div
                                    className="relative w-full overflow-hidden rounded-md bg-primary/15"
                                    style={{ height: "100%" }}
                                >
                                    <div
                                        className="absolute bottom-0 left-0 right-0 bg-primary transition-all"
                                        style={{ height: `${heightPct}%` }}
                                        aria-label={`${point.date}: ${(
                                            point.averageQualityScore * 100
                                        ).toFixed(1)}%`}
                                    />
                                </div>
                                <div className="text-center text-[10px] leading-tight text-muted-foreground">
                                    <div>{point.date.slice(5)}</div>
                                    <div className="tabular-nums">
                                        {(point.averageQualityScore * 100).toFixed(0)}%
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
