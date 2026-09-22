import { ApiClient } from "@/lib/api/abstractions/api-client.interface";
import { AnalysisService } from "../../application/abstractions/analysis-service.interface";
import {
    AnalysisDetail,
    AnalysisList,
} from "../../domain/models/analysis.model";

export class HttpAnalysisService implements AnalysisService {
    constructor(private readonly apiClient: ApiClient) {}

    async list(): Promise<AnalysisList> {
        return this.apiClient.request<AnalysisList>("/analysis/runs");
    }

    async getById(id: string): Promise<AnalysisDetail> {
        return this.apiClient.request<AnalysisDetail>(
            `/analysis/runs/${encodeURIComponent(id)}`,
        );
    }
}
