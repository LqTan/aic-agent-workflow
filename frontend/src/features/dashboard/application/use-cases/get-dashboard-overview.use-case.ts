import { DashboardOverview } from "../../domain/models/dashboard.model";
import { DashboardService } from "../abstractions/dashboard-service.interface";

export class GetDashboardOverviewUseCase {
    constructor(
        private readonly dashboardService: DashboardService,
    ) {}

    async execute(): Promise<DashboardOverview> {
        return this.dashboardService.getOverview();
    }
}
