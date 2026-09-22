import type { VideoSearchResponse } from "@/features/video-search/domain/models/video-search.model";
import {
    alternativeSearchResponses,
    baseSearchResponse,
} from "@/features/video-search/infrastructure/mocks/fixtures/video-search.fixtures";
import type {
    AnalysisDetail,
    AnalysisList,
    AnalysisRunSummary,
} from "../../../domain/models/analysis.model";

const isoDaysAgo = (days: number, hour = 9, minute = 0): string => {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    date.setUTCHours(hour, minute, 0, 0);
    return date.toISOString();
};

const buildSummary = (
    id: string,
    daysAgo: number,
    response: VideoSearchResponse,
    durationMs: number,
    collectionIds: string[],
): AnalysisRunSummary => ({
    id,
    goal: response.goal,
    query: response.plan.searchQuery,
    timestamp: isoDaysAgo(daysAgo, 9 + daysAgo, daysAgo * 5),
    qualityScore: response.qualityScore,
    decision: response.decision,
    resultCount: response.count,
    attempts: response.attempts.length,
    durationMs,
    collectionIds,
    planner: response.plan.planner,
});

export const analysisRunsFixture: AnalysisRunSummary[] = [
    buildSummary("run_0001", 0, baseSearchResponse, 1820, [
        "street_videos_2024",
    ]),
    buildSummary("run_0002", 0, alternativeSearchResponses[0], 980, [
        "classroom_videos_2024",
    ]),
    buildSummary("run_0003", 1, alternativeSearchResponses[1], 1340, [
        "classroom_videos_2024",
    ]),
];

const variantForRun = (runId: string): AnalysisDetail => {
    if (runId === "run_0002") {
        return alternativeSearchResponses[0];
    }

    if (runId === "run_0003") {
        return alternativeSearchResponses[1];
    }

    return baseSearchResponse;
};

export const analysisListFixture: AnalysisList = {
    total: analysisRunsFixture.length,
    runs: analysisRunsFixture,
};

export const buildAnalysisDetailFixture = (
    runId: string,
): AnalysisDetail => ({
    ...variantForRun(runId),
    goal:
        analysisRunsFixture.find((run) => run.id === runId)?.goal ??
        variantForRun(runId).goal,
});
