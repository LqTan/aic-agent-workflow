import { PageHeader } from "@/components/layout/page-header";
import { AnalysisListPage } from "@/features/analysis/presentation/components/analysis-list-page";

export default function AnalysisPage() {
    return (
        <>
            <PageHeader
                title="Analysis"
                description="Phân tích chi tiết từng lần chạy"
            />
            <AnalysisListPage />
        </>
    );
}
