"use client";

import { useEffect, useState } from "react";
import { DashboardOverview } from "../../domain/models/dashboard.model";
import { getDashboardOverviewUseCase } from "../../dependency-injection";

interface DashboardState {
    data: DashboardOverview | null;
    isLoading: boolean;
    error: Error | null;
}

const initialState: DashboardState = {
    data: null,
    isLoading: true,
    error: null,
};

export function useDashboardOverview(): DashboardState {
    const [state, setState] = useState<DashboardState>(initialState);

    useEffect(() => {
        let cancelled = false;

        const load = async (): Promise<void> => {
            try {
                const data = await getDashboardOverviewUseCase.execute();
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
                                : new Error("Failed to load dashboard"),
                    });
                }
            }
        };

        void load();

        return () => {
            cancelled = true;
        };
    }, []);

    return state;
}
