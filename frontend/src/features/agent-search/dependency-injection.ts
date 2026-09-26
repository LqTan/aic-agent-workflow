import { N8nAgentSearchService } from "./infrastructure/services/n8n-agent-search.service";
import { RunAgentSearchUseCase } from "./application/use-cases/run-agent-search.use-case";

const service = new N8nAgentSearchService();

export const runAgentSearchUseCase = new RunAgentSearchUseCase(service);