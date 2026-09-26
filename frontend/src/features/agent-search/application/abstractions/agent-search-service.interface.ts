import type {
    AgentSearchRequest,
    AgentSearchResponse,
} from "../../domain/models/agent-search.model";

export interface AgentSearchService {
    search(request: AgentSearchRequest): Promise<AgentSearchResponse>;
}