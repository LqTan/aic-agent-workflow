import { PageHeader } from "@/components/layout/page-header";
import { RunDetailClient } from "./run-detail-client";

export const dynamic = "force-static";

export async function generateStaticParams(): Promise<{ runId: string }[]> {
    return [{ runId: "_placeholder" }];
}

export default function RunDetailPage() {
    return (
        <>
            <PageHeader
                title="Run detail"
                description="Phân tích một lần chạy"
            />
            <RunDetailClient />
        </>
    );
}
