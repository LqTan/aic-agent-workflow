import { AnalysisDetail } from "../../domain/models/analysis.model";
import { AnalysisService } from "../abstractions/analysis-service.interface";

export class GetAnalysisDetailUseCase {
    constructor(
        private readonly analysisService: AnalysisService,
    ) {}

    async execute(runId: string): Promise<AnalysisDetail> {
        const normalized = runId.trim();

        if (!normalized) {
            throw new Error("Run id is required.");
        }

        return this.analysisService.getById(normalized);
    }
}
