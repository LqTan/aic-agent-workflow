import { env } from "@/config/env";
import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { GetEvaluationOverviewUseCase } from "./application/use-cases/get-evaluation-overview.use-case";
import { HttpEvaluationService } from "./infrastructure/services/http-evaluation.service";
import { MockEvaluationService } from "./infrastructure/mocks/services/mock-evaluation.service";

const evaluationService = env.useMocks
    ? new MockEvaluationService()
    : new HttpEvaluationService(new FetchApiClient());

export const getEvaluationOverviewUseCase = new GetEvaluationOverviewUseCase(
    evaluationService,
);
