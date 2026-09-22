import type {
    DashboardOverview,
    SearchRunSummary,
} from "../../../domain/models/dashboard.model";

const isoDaysAgo = (days: number): string => {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    return date.toISOString();
};

const isoDate = (days: number): string => {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    return date.toISOString().slice(0, 10);
};

export const recentRunsFixture: SearchRunSummary[] = [
    {
        id: "run_0001",
        goal: "Tìm cảnh một người đang đi xe đạp ngoài đường",
        query: "Tìm cảnh một người đang đi xe đạp ngoài đường",
        timestamp: isoDaysAgo(0),
        qualityScore: 0.78,
        attempts: 2,
        decision: "accepted",
        resultCount: 12,
        durationMs: 1820,
    },
    {
        id: "run_0002",
        goal: "Tìm cảnh giáo viên giảng bài trên bảng",
        query: "Tìm cảnh giáo viên giảng bài trên bảng",
        timestamp: isoDaysAgo(0),
        qualityScore: 0.48,
        attempts: 1,
        decision: "accepted",
        resultCount: 12,
        durationMs: 980,
    },
    {
        id: "run_0003",
        goal: "Tìm cảnh học sinh viết bài trong lớp",
        query: "Tìm cảnh học sinh viết bài trong lớp",
        timestamp: isoDaysAgo(1),
        qualityScore: 0.39,
        attempts: 2,
        decision: "best_effort",
        resultCount: 12,
        durationMs: 1340,
    },
    {
        id: "run_0004",
        goal: "Tìm cảnh học sinh giơ tay phát biểu",
        query: "Tìm cảnh học sinh giơ tay phát biểu",
        timestamp: isoDaysAgo(1),
        qualityScore: 0.66,
        attempts: 1,
        decision: "accepted",
        resultCount: 10,
        durationMs: 880,
    },
    {
        id: "run_0005",
        goal: "Tìm cảnh bác sĩ khám bệnh nhân trong bệnh viện",
        query: "Tìm cảnh bác sĩ khám bệnh nhân trong bệnh viện",
        timestamp: isoDaysAgo(2),
        qualityScore: 0.54,
        attempts: 1,
        decision: "accepted",
        resultCount: 12,
        durationMs: 1020,
    },
    {
        id: "run_0006",
        goal: "Tìm cảnh đầu bếp nấu ăn trong nhà hàng",
        query: "Tìm cảnh đầu bếp nấu ăn trong nhà hàng",
        timestamp: isoDaysAgo(2),
        qualityScore: 0.41,
        attempts: 2,
        decision: "best_effort",
        resultCount: 9,
        durationMs: 1480,
    },
    {
        id: "run_0007",
        goal: "Tìm cảnh cầu thủ đá bóng trên sân",
        query: "Tìm cảnh cầu thủ đá bóng trên sân",
        timestamp: isoDaysAgo(3),
        qualityScore: 0.71,
        attempts: 1,
        decision: "accepted",
        resultCount: 12,
        durationMs: 920,
    },
];

export const qualityTrendFixture = [
    { date: isoDate(6), averageQualityScore: 0.52, queryCount: 14 },
    { date: isoDate(5), averageQualityScore: 0.58, queryCount: 18 },
    { date: isoDate(4), averageQualityScore: 0.61, queryCount: 22 },
    { date: isoDate(3), averageQualityScore: 0.55, queryCount: 19 },
    { date: isoDate(2), averageQualityScore: 0.49, queryCount: 16 },
    { date: isoDate(1), averageQualityScore: 0.63, queryCount: 21 },
    { date: isoDate(0), averageQualityScore: 0.66, queryCount: 24 },
];

export const dashboardOverviewFixture: DashboardOverview = {
    totalQueries: 134,
    acceptedQueries: 96,
    bestEffortQueries: 38,
    averageQualityScore: 0.58,
    averageAttempts: 1.42,
    averageDurationMs: 1180,
    totalIndexedVideos: 4280,
    totalCollections: 12,
    lastUpdatedAt: new Date().toISOString(),
    recentRuns: recentRunsFixture,
    qualityTrend: qualityTrendFixture,
};
