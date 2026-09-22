"use client";

import { useParams } from "next/navigation";
import { PageHeader } from "@/components/layout/page-header";
import { AnalysisDetailPage } from "@/features/analysis/presentation/components/analysis-detail-page";

export default function RunDetailPage() {
    const params = useParams<{ runId: string }>();
    const runId = params?.runId ?? "";

    return (
        <>
            <PageHeader
                title="Run detail"
                description="Phân tích một lần chạy"
            />
            <AnalysisDetailPage runId={runId} />
        </>
    );
}
