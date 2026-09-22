import { HistoryFilter, HistoryList } from "../../domain/models/history.model";

export interface HistoryService {
    list(filter?: HistoryFilter): Promise<HistoryList>;
}
