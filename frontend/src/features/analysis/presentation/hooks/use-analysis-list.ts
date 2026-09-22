"use client";

import { useEffect, useState } from "react";
import { AnalysisList } from "../../domain/models/analysis.model";
import { getAnalysisListUseCase } from "../../dependency-injection";

interface AnalysisListState {
    data: AnalysisList | null;
    isLoading: boolean;
    error: Error | null;
}

const initialState: AnalysisListState = {
    data: null,
    isLoading: true,
    error: null,
};

export function useAnalysisList(): AnalysisListState {
    const [state, setState] = useState<AnalysisListState>(initialState);

    useEffect(() => {
        let cancelled = false;

        const load = async (): Promise<void> => {
            try {
                const data = await getAnalysisListUseCase.execute();
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
                                : new Error("Failed to load runs"),
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
