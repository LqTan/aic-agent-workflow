import { env } from "@/config/env";
import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { GetDashboardOverviewUseCase } from "./application/use-cases/get-dashboard-overview.use-case";
import { HttpDashboardService } from "./infrastructure/services/http-dashboard.service";
import { MockDashboardService } from "./infrastructure/mocks/services/mock-dashboard.service";

const dashboardService = env.useMocks
    ? new MockDashboardService()
    : new HttpDashboardService(new FetchApiClient());

export const getDashboardOverviewUseCase =
    new GetDashboardOverviewUseCase(dashboardService);
