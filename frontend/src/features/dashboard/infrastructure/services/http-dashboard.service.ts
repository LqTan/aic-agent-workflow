import { ApiClient } from "@/lib/api/abstractions/api-client.interface";
import { DashboardService } from "../../application/abstractions/dashboard-service.interface";
import { DashboardOverview } from "../../domain/models/dashboard.model";

export class HttpDashboardService implements DashboardService {
    constructor(private readonly apiClient: ApiClient) {}

    async getOverview(): Promise<DashboardOverview> {
        return this.apiClient.request<DashboardOverview>(
            "/api/dashboard/overview",
        );
    }
}
