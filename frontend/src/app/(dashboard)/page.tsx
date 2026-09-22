import { PageHeader } from "@/components/layout/page-header";
import { Dashboard } from "@/features/dashboard/presentation/components/dashboard";

export default function DashboardPage() {
    return (
        <>
            <PageHeader
                title="Dashboard"
                description="Tổng quan hệ thống AI Agent"
            />
            <Dashboard />
        </>
    );
}
