import { DashboardService } from "../../../application/abstractions/dashboard-service.interface";
import { DashboardOverview } from "../../../domain/models/dashboard.model";
import { dashboardOverviewFixture } from "../fixtures/dashboard.fixtures";

const wait = (ms: number): Promise<void> =>
    new Promise((resolve) => setTimeout(resolve, ms));

export class MockDashboardService implements DashboardService {
    async getOverview(): Promise<DashboardOverview> {
        await wait(300);
        return {
            ...dashboardOverviewFixture,
            lastUpdatedAt: new Date().toISOString(),
        };
    }
}
