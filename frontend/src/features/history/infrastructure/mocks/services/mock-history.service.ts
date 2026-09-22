import { HistoryService } from "../../../application/abstractions/history-service.interface";
import { HistoryFilter, HistoryList } from "../../../domain/models/history.model";
import { historyListFixture } from "../fixtures/history.fixtures";

const wait = (ms: number): Promise<void> =>
    new Promise((resolve) => setTimeout(resolve, ms));

export class MockHistoryService implements HistoryService {
    async list(filter?: HistoryFilter): Promise<HistoryList> {
        await wait(280);

        const decision = filter?.decision ?? "all";
        const query = filter?.query?.trim().toLowerCase() ?? "";

        const filtered = historyListFixture.entries.filter((entry) => {
            if (decision !== "all" && entry.decision !== decision) {
                return false;
            }

            if (
                query &&
                !entry.goal.toLowerCase().includes(query) &&
                !entry.query.toLowerCase().includes(query)
            ) {
                return false;
            }

            return true;
        });

        return {
            total: filtered.length,
            entries: filtered,
        };
    }
}
