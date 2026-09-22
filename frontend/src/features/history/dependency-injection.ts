import { env } from "@/config/env";
import { FetchApiClient } from "@/lib/api/fetch-api-client";
import { GetHistoryUseCase } from "./application/use-cases/get-history.use-case";
import { HttpHistoryService } from "./infrastructure/services/http-history.service";
import { MockHistoryService } from "./infrastructure/mocks/services/mock-history.service";

const historyService = env.useMocks
    ? new MockHistoryService()
    : new HttpHistoryService(new FetchApiClient());

export const getHistoryUseCase = new GetHistoryUseCase(historyService);
