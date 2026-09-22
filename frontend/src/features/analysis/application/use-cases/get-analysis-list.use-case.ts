import { AnalysisList } from "../../domain/models/analysis.model";
import { AnalysisService } from "../abstractions/analysis-service.interface";

export class GetAnalysisListUseCase {
    constructor(
        private readonly analysisService: AnalysisService,
    ) {}

    async execute(): Promise<AnalysisList> {
        return this.analysisService.list();
    }
}
