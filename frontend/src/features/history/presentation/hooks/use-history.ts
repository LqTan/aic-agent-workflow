"use client";

import { useEffect, useMemo, useState } from "react";
import {
    HistoryFilter,
    HistoryList,
} from "../../domain/models/history.model";
import { getHistoryUseCase } from "../../dependency-injection";

interface HistoryState {
    data: HistoryList | null;
    isLoading: boolean;
    error: Error | null;
}

const initialState: HistoryState = {
    data: null,
    isLoading: true,
    error: null,
};

export function useHistory(filter: HistoryFilter = {}): HistoryState {
    const [state, setState] = useState<HistoryState>(initialState);

    const filterKey = useMemo(
        () =>
            JSON.stringify({
                decision: filter.decision ?? "all",
                query: filter.query ?? "",
            }),
        [filter.decision, filter.query],
    );

    useEffect(() => {
        let cancelled = false;

        const load = async (): Promise<void> => {
            try {
                setState((prev) => ({ ...prev, isLoading: true }));
                const data = await getHistoryUseCase.execute({
                    decision: filter.decision,
                    query: filter.query,
                });

                if (!cancelled) {
                    setState({ data, isLoading: false, error: null });
                }
            } catch (error) {
                if (!cancelled) {
                    setState({
                        data: null,
                        isLoading: false,
                        error:
                            error instanceof Error
                                ? error
                                : new Error("Failed to load history"),
                    });
                }
            }
        };

        void load();

        return () => {
            cancelled = true;
        };
    }, [filterKey, filter.decision, filter.query]);

    return state;
}
