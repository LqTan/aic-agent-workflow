import { env } from "@/config/env";
import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { GetAnalysisDetailUseCase } from "./application/use-cases/get-analysis-detail.use-case";
import { GetAnalysisListUseCase } from "./application/use-cases/get-analysis-list.use-case";
import { HttpAnalysisService } from "./infrastructure/services/http-analysis.service";
import { MockAnalysisService } from "./infrastructure/mocks/services/mock-analysis.service";

const analysisService = env.useMocks
    ? new MockAnalysisService()
    : new HttpAnalysisService(new FetchApiClient());

export const getAnalysisListUseCase = new GetAnalysisListUseCase(
    analysisService,
);
export const getAnalysisDetailUseCase = new GetAnalysisDetailUseCase(
    analysisService,
);
