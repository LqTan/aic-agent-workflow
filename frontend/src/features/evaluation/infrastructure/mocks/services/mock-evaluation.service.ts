import { EvaluationService } from "../../../application/abstractions/evaluation-service.interface";
import { EvaluationOverview } from "../../../domain/models/evaluation.model";
import { evaluationOverviewFixture } from "../fixtures/evaluation.fixtures";

const wait = (ms: number): Promise<void> =>
    new Promise((resolve) => setTimeout(resolve, ms));

export class MockEvaluationService implements EvaluationService {
    async getOverview(): Promise<EvaluationOverview> {
        await wait(280);
        return evaluationOverviewFixture();
    }
}
