import { GetDashboardOverviewUseCase } from "./application/use-cases/get-dashboard-overview.use-case";
import { MockDashboardService } from "./infrastructure/mocks/services/mock-dashboard.service";

const dashboardService = new MockDashboardService();

export const getDashboardOverviewUseCase =
    new GetDashboardOverviewUseCase(dashboardService);
