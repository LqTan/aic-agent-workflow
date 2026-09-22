import { HistoryFilter, HistoryList } from "../../domain/models/history.model";
import { HistoryService } from "../abstractions/history-service.interface";

export class GetHistoryUseCase {
    constructor(
        private readonly historyService: HistoryService,
    ) {}

    async execute(filter?: HistoryFilter): Promise<HistoryList> {
        return this.historyService.list(filter);
    }
}
