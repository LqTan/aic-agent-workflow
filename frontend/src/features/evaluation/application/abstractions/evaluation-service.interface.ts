import { EvaluationOverview } from "../../domain/models/evaluation.model";

export interface EvaluationService {
    getOverview(): Promise<EvaluationOverview>;
}
