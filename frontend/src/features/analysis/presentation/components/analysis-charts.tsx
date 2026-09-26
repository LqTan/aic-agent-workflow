"use client";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    Tooltip,
    XAxis,
    YAxis,
    ZAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisRunSummary } from "../../domain/models/analysis.model";

interface AnalysisChartsProps {
    runs: AnalysisRunSummary[];
}

const CHART_COLORS = {
    primary: "oklch(0.205 0 0)",
    accent: "oklch(0.488 0.243 264.376)",
    success: "oklch(0.6 0.15 145)",
    warning: "oklch(0.7 0.18 65)",
    danger: "oklch(0.577 0.245 27.325)",
    muted: "oklch(0.708 0 0)",
    grid: "oklch(0.922 0 0)",
};

const formatShortTime = (iso: string): string => {
    const date = new Date(iso);
    return `${date.getHours().toString().padStart(2, "0")}:${date
        .getMinutes()
        .toString()
        .padStart(2, "0")} ${date.getMonth() + 1}/${date.getDate()}`;
};

const tooltipStyle = {
    backgroundColor: "var(--popover)",
    borderColor: "var(--border)",
    borderRadius: "8px",
    color: "var(--popover-foreground)",
    fontSize: "12px",
} as const;

export function AnalysisCharts({ runs }: AnalysisChartsProps) {
    if (runs.length === 0) {
        return null;
    }

    const sortedByTime = [...runs].sort(
        (a, b) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
    );

    const qualitySeries = sortedByTime.map((run, index) => ({
        index: index + 1,
        label: formatShortTime(run.timestamp),
        quality: Number((run.qualityScore * 100).toFixed(1)),
        decision: run.decision,
    }));

    const decisionCounts = runs.reduce<Record<string, number>>(
        (acc, run) => {
            acc[run.decision] = (acc[run.decision] ?? 0) + 1;
            return acc;
        },
        {},
    );

    const decisionData = [
        {
            name: "Accepted",
            value: decisionCounts.accepted ?? 0,
            color: CHART_COLORS.success,
        },
        {
            name: "Best effort",
            value: decisionCounts["best_effort"] ?? 0,
            color: CHART_COLORS.warning,
        },
    ];

    const latencyQuality = runs.map((run, index) => ({
        index: index + 1,
        latency: Number((run.durationMs / 1000).toFixed(2)),
        quality: Number((run.qualityScore * 100).toFixed(1)),
        decision: run.decision,
    }));

    const attemptsData = sortedByTime.map((run, index) => ({
        index: index + 1,
        label: formatShortTime(run.timestamp),
        attempts: run.attempts,
        results: run.resultCount,
    }));

    return (
        <div className="grid gap-4 lg:grid-cols-2">
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">
                        Quality theo thời gian
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-56 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={qualitySeries}>
                                <CartesianGrid
                                    stroke={CHART_COLORS.grid}
                                    strokeDasharray="3 3"
                                />
                                <XAxis
                                    dataKey="label"
                                    tick={{ fontSize: 11, fill: CHART_COLORS.muted }}
                                    stroke={CHART_COLORS.muted}
                                />
                                <YAxis
                                    domain={[0, 100]}
                                    tickFormatter={(value: number) => `${value}%`}
                                    tick={{ fontSize: 11, fill: CHART_COLORS.muted }}
                                    stroke={CHART_COLORS.muted}
                                />
                                <Tooltip
                                    contentStyle={tooltipStyle}
                                    formatter={(value: number) => [`${value}%`, "Quality"]}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="quality"
                                    stroke={CHART_COLORS.primary}
                                    strokeWidth={2}
                                    dot={{ r: 3, fill: CHART_COLORS.primary }}
                                    activeDot={{ r: 5 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Phân bố decision</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-56 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Tooltip
                                    contentStyle={tooltipStyle}
                                    formatter={(value: number, name: string) => [
                                        value,
                                        name,
                                    ]}
                                />
                                <Legend
                                    wrapperStyle={{ fontSize: "12px" }}
                                    iconType="circle"
                                />
                                <Pie
                                    data={decisionData}
                                    dataKey="value"
                                    nameKey="name"
                                    innerRadius={50}
                                    outerRadius={80}
                                    paddingAngle={2}
                                >
                                    {decisionData.map((entry) => (
                                        <Cell
                                            key={entry.name}
                                            fill={entry.color}
                                            stroke="var(--background)"
                                            strokeWidth={2}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-base">
                        Latency vs Quality
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-56 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart>
                                <CartesianGrid
                                    stroke={CHART_COLORS.grid}
                                    strokeDasharray="3 3"
                                />
                                <XAxis
                                    type="number"
                                    dataKey="latency"
                                    name="Latency"
                                    unit="s"
                                    tick={{ fontSize: 11, fill: CHART_COLORS.muted }}
                                    stroke={CHART_COLORS.muted}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="quality"
                                    name="Quality"
                                    unit="%"
                                    domain={[0, 100]}
                                    tick={{ fontSize: 11, fill: CHART_COLORS.muted }}
                                    stroke={CHART_COLORS.muted}
                                />
                                <ZAxis range={[60, 60]} />
                                <Tooltip
                                    contentStyle={tooltipStyle}
                                    cursor={{ strokeDasharray: "3 3" }}
                                    formatter={(value: number, name: string) => [
                                        name === "Quality"
                                            ? `${value}%`
                                            : `${value}s`,
                                        name,
                                    ]}
                                />
                                <Scatter
                                    data={latencyQuality}
                                    fill={CHART_COLORS.accent}
                                />
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Attempts & Results</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-56 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={attemptsData}>
                                <CartesianGrid
                                    stroke={CHART_COLORS.grid}
                                    strokeDasharray="3 3"
                                />
                                <XAxis
                                    dataKey="label"
                                    tick={{ fontSize: 11, fill: CHART_COLORS.muted }}
                                    stroke={CHART_COLORS.muted}
                                />
                                <YAxis
                                    allowDecimals={false}
                                    tick={{ fontSize: 11, fill: CHART_COLORS.muted }}
                                    stroke={CHART_COLORS.muted}
                                />
                                <Tooltip
                                    contentStyle={tooltipStyle}
                                    cursor={{ fill: "var(--muted)" }}
                                />
                                <Legend
                                    wrapperStyle={{ fontSize: "12px" }}
                                    iconType="rect"
                                />
                                <Bar
                                    dataKey="attempts"
                                    name="Attempts"
                                    fill={CHART_COLORS.primary}
                                    radius={[4, 4, 0, 0]}
                                />
                                <Bar
                                    dataKey="results"
                                    name="Results"
                                    fill={CHART_COLORS.accent}
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}