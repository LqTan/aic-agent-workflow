"use client";

import { useParams } from "next/navigation";

import { AnalysisDetailPage } from "@/features/analysis/presentation/components/analysis-detail-page";

export function RunDetailClient() {
    const params = useParams<{ runId: string }>();
    const runId = params?.runId ?? "";

    return <AnalysisDetailPage runId={runId} />;
}
