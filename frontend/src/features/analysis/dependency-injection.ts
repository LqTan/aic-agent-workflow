import { GetAnalysisDetailUseCase } from "./application/use-cases/get-analysis-detail.use-case";
import { GetAnalysisListUseCase } from "./application/use-cases/get-analysis-list.use-case";
import { MockAnalysisService } from "./infrastructure/mocks/services/mock-analysis.service";

const analysisService = new MockAnalysisService();

export const getAnalysisListUseCase = new GetAnalysisListUseCase(
    analysisService,
);

export const getAnalysisDetailUseCase = new GetAnalysisDetailUseCase(
    analysisService,
);
