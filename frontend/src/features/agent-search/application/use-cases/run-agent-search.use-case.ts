import type {
    AgentSearchRequest,
    AgentSearchResponse,
} from "../../domain/models/agent-search.model";
import type { AgentSearchService } from "../abstractions/agent-search-service.interface";

export class RunAgentSearchUseCase {
    constructor(private readonly service: AgentSearchService) {}

    async execute(request: AgentSearchRequest): Promise<AgentSearchResponse> {
        const query = request.query.trim();
        if (!query) {
            throw new Error("Query không được rỗng.");
        }
        return this.service.search({ ...request, query });
    }
}