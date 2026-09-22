import type {
    EvaluationOverview,
    EvaluationRun,
    QualityBucket,
} from "../../../domain/models/evaluation.model";

const isoDaysAgo = (days: number, hour = 9, minute = 0): string => {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    date.setUTCHours(hour, minute, 0, 0);
    return date.toISOString();
};

export const evaluationRunsFixture: EvaluationRun[] = [
    {
        id: "run_0001",
        goal: "Tìm cảnh một người đang đi xe đạp ngoài đường",
        query: "person riding bicycle on street outdoor",
        timestamp: isoDaysAgo(0, 14, 12),
        qualityScore: 0.78,
        threshold: 0.42,
        attempts: 2,
        decision: "accepted",
        resultCount: 12,
        latencyMs: 1820,
        collectionIds: ["street_videos_2024"],
    },
    {
        id: "run_0002",
        goal: "Tìm cảnh giáo viên giảng bài trên bảng",
        query: "teacher explaining whiteboard classroom",
        timestamp: isoDaysAgo(0, 10, 30),
        qualityScore: 0.48,
        threshold: 0.42,
        attempts: 1,
        decision: "accepted",
        resultCount: 12,
        latencyMs: 980,
        collectionIds: ["classroom_videos_2024"],
    },
    {
        id: "run_0003",
        goal: "Tìm cảnh học sinh viết bài trong lớp",
        query: "student writing notebook classroom",
        timestamp: isoDaysAgo(1, 16, 5),
        qualityScore: 0.39,
        threshold: 0.42,
        attempts: 2,
        decision: "best_effort",
        resultCount: 12,
        latencyMs: 1340,
        collectionIds: ["classroom_videos_2024"],
    },
    {
        id: "run_0004",
        goal: "Tìm cảnh học sinh giơ tay phát biểu",
        query: "student raising hand classroom",
        timestamp: isoDaysAgo(1, 11, 15),
        qualityScore: 0.66,
        threshold: 0.42,
        attempts: 1,
        decision: "accepted",
        resultCount: 10,
        latencyMs: 880,
        collectionIds: ["classroom_videos_2024"],
    },
    {
        id: "run_0005",
        goal: "Tìm cảnh bác sĩ khám bệnh nhân trong bệnh viện",
        query: "doctor examining patient hospital",
        timestamp: isoDaysAgo(2, 9, 45),
        qualityScore: 0.54,
        threshold: 0.42,
        attempts: 1,
        decision: "accepted",
        resultCount: 12,
        latencyMs: 1020,
        collectionIds: ["hospital_videos_2024"],
    },
    {
        id: "run_0006",
        goal: "Tìm cảnh đầu bếp nấu ăn trong nhà hàng",
        query: "chef cooking kitchen restaurant",
        timestamp: isoDaysAgo(2, 14, 20),
        qualityScore: 0.41,
        threshold: 0.42,
        attempts: 2,
        decision: "best_effort",
        resultCount: 9,
        latencyMs: 1480,
        collectionIds: ["kitchen_videos_2024"],
    },
    {
        id: "run_0007",
        goal: "Tìm cảnh cầu thủ đá bóng trên sân",
        query: "soccer player kicking ball stadium",
        timestamp: isoDaysAgo(3, 17, 10),
        qualityScore: 0.71,
        threshold: 0.42,
        attempts: 1,
        decision: "accepted",
        resultCount: 12,
        latencyMs: 920,
        collectionIds: ["sports_videos_2024"],
    },
    {
        id: "run_0008",
        goal: "Tìm cảnh phi công lái máy bay trong buồng lái",
        query: "pilot cockpit airplane",
        timestamp: isoDaysAgo(3, 12, 0),
        qualityScore: 0.62,
        threshold: 0.42,
        attempts: 1,
        decision: "accepted",
        resultCount: 11,
        latencyMs: 1100,
        collectionIds: ["aviation_videos_2024"],
    },
];

const buildBuckets = (runs: EvaluationRun[]): QualityBucket[] => {
    const buckets: QualityBucket[] = [
        { bucket: "0-20%", min: 0, max: 0.2, count: 0 },
        { bucket: "20-40%", min: 0.2, max: 0.4, count: 0 },
        { bucket: "40-60%", min: 0.4, max: 0.6, count: 0 },
        { bucket: "60-80%", min: 0.6, max: 0.8, count: 0 },
        { bucket: "80-100%", min: 0.8, max: 1.01, count: 0 },
    ];

    for (const run of runs) {
        const target = buckets.find(
            (bucket) =>
                run.qualityScore >= bucket.min &&
                run.qualityScore < bucket.max,
        );
        if (target) {
            target.count += 1;
        }
    }

    return buckets;
};

export const evaluationOverviewFixture = (
    runs: EvaluationRun[] = evaluationRunsFixture,
): EvaluationOverview => {
    const totalQuality = runs.reduce((acc, run) => acc + run.qualityScore, 0);
    const totalAttempts = runs.reduce((acc, run) => acc + run.attempts, 0);
    const totalLatency = runs.reduce((acc, run) => acc + run.latencyMs, 0);

    return {
        totalRuns: runs.length,
        averageQuality: runs.length ? totalQuality / runs.length : 0,
        averageAttempts: runs.length ? totalAttempts / runs.length : 0,
        averageLatency: runs.length ? totalLatency / runs.length : 0,
        thresholdDefault: 0.42,
        decisionDistribution: {
            accepted: runs.filter((run) => run.decision === "accepted").length,
            bestEffort: runs.filter((run) => run.decision === "best_effort")
                .length,
        },
        qualityDistribution: buildBuckets(runs),
        runs,
    };
};
