import { DashboardOverview } from "../../domain/models/dashboard.model";

export interface DashboardService {
    getOverview(): Promise<DashboardOverview>;
}
