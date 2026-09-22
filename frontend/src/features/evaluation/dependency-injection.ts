import { GetEvaluationOverviewUseCase } from "./application/use-cases/get-evaluation-overview.use-case";
import { MockEvaluationService } from "./infrastructure/mocks/services/mock-evaluation.service";

const evaluationService = new MockEvaluationService();

export const getEvaluationOverviewUseCase =
    new GetEvaluationOverviewUseCase(evaluationService);
