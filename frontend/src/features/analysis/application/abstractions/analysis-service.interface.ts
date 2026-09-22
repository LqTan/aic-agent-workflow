import type {
    AnalysisDetail,
    AnalysisList,
} from "../../domain/models/analysis.model";

export interface AnalysisService {
    list(): Promise<AnalysisList>;
    getById(id: string): Promise<AnalysisDetail>;
}
