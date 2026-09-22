import { PageHeader } from "@/components/layout/page-header";
import { EvaluationPage } from "@/features/evaluation/presentation/components/evaluation-page";

export default function EvaluationPageRoute() {
    return (
        <>
            <PageHeader
                title="Evaluation"
                description="Đánh giá retrieval và quality scoring"
            />
            <EvaluationPage />
        </>
    );
}
