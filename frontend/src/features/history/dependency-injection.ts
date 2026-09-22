import { GetHistoryUseCase } from "./application/use-cases/get-history.use-case";
import { MockHistoryService } from "./infrastructure/mocks/services/mock-history.service";

const historyService = new MockHistoryService();

export const getHistoryUseCase = new GetHistoryUseCase(historyService);
