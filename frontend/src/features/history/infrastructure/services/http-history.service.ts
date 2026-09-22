import { ApiClient } from "@/lib/api/abstractions/api-client.interface";
import { HistoryService } from "../../application/abstractions/history-service.interface";
import {
    HistoryFilter,
    HistoryList,
} from "../../domain/models/history.model";

export class HttpHistoryService implements HistoryService {
    constructor(private readonly apiClient: ApiClient) {}

    async list(filter?: HistoryFilter): Promise<HistoryList> {
        const params = new URLSearchParams();
        if (filter?.decision) params.set("decision", filter.decision);
        if (filter?.query) params.set("query", filter.query);
        params.set("limit", "100");
        const query = params.toString();
        return this.apiClient.request<HistoryList>(
            `/history/?${query}`,
        );
    }
}
