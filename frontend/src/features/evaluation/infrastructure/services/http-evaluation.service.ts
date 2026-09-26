import { ApiClient } from "@/lib/api/abstractions/api-client.interface";
import { EvaluationService } from "../../application/abstractions/evaluation-service.interface";
import { EvaluationOverview } from "../../domain/models/evaluation.model";

export class HttpEvaluationService implements EvaluationService {
    constructor(private readonly apiClient: ApiClient) {}

    async getOverview(): Promise<EvaluationOverview> {
        return this.apiClient.request<EvaluationOverview>(
            "/evaluation/overview",
        );
    }
}
