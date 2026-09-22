import { EvaluationOverview } from "../../domain/models/evaluation.model";
import { EvaluationService } from "../abstractions/evaluation-service.interface";

export class GetEvaluationOverviewUseCase {
    constructor(
        private readonly evaluationService: EvaluationService,
    ) {}

    async execute(): Promise<EvaluationOverview> {
        return this.evaluationService.getOverview();
    }
}
