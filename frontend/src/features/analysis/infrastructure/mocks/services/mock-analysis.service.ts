import { AnalysisService } from "../../../application/abstractions/analysis-service.interface";
import {
    AnalysisDetail,
    AnalysisList,
} from "../../../domain/models/analysis.model";
import {
    analysisListFixture,
    buildAnalysisDetailFixture,
} from "../fixtures/analysis.fixtures";

const wait = (ms: number): Promise<void> =>
    new Promise((resolve) => setTimeout(resolve, ms));

export class MockAnalysisService implements AnalysisService {
    async list(): Promise<AnalysisList> {
        await wait(280);
        return analysisListFixture;
    }

    async getById(id: string): Promise<AnalysisDetail> {
        await wait(420);

        const exists = analysisListFixture.runs.some((run) => run.id === id);

        if (!exists) {
            throw new Error(`Run "${id}" was not found.`);
        }

        return buildAnalysisDetailFixture(id);
    }
}
