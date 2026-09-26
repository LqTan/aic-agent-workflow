import { PageHeader } from "@/components/layout/page-header";
import { AgentSearch } from "@/features/agent-search/presentation/components/agent-search";

export default function AgentSearchPage() {
    return (
        <>
            <PageHeader
                title="Agent Search via n8n"
                description="Gọi workflow AIC Agentic Video Retrieval trên n8n (port 5678) — Planner → Retrieval → Validation → Persist → Finalize"
            />
            <AgentSearch />
        </>
    );
}