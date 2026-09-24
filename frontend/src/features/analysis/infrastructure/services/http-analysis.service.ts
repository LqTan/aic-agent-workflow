import { ApiClient } from "@/lib/api/abstractions/api-client.interface";
import { AnalysisService } from "../../application/abstractions/analysis-service.interface";
import {
    AnalysisDetail,
    AnalysisList,
} from "../../domain/models/analysis.model";

export class HttpAnalysisService implements AnalysisService {
    constructor(private readonly apiClient: ApiClient) {}

    async list(): Promise<AnalysisList> {
        return this.apiClient.request<AnalysisList>("/api/analysis/runs");
    }

    async getById(id: string): Promise<AnalysisDetail> {
        return this.apiClient.request<AnalysisDetail>(
            `/api/analysis/runs/${encodeURIComponent(id)}`,
        );
    }
}
