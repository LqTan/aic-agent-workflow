import { PageHeader } from "@/components/layout/page-header";
import { HistoryList } from "@/features/history/presentation/components/history-list";

export default function HistoryPage() {
    return (
        <>
            <PageHeader
                title="Query History"
                description="Lịch sử truy vấn"
            />
            <HistoryList />
        </>
    );
}
