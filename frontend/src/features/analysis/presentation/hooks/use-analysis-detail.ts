"use client";

import { useEffect, useState } from "react";
import { AnalysisDetail } from "../../domain/models/analysis.model";
import { getAnalysisDetailUseCase } from "../../dependency-injection";

interface AnalysisDetailState {
    data: AnalysisDetail | null;
    isLoading: boolean;
    error: Error | null;
}

const initialState: AnalysisDetailState = {
    data: null,
    isLoading: true,
    error: null,
};

const missingRunIdState: AnalysisDetailState = {
    data: null,
    isLoading: false,
    error: new Error("Missing run id"),
};

export function useAnalysisDetail(runId: string): AnalysisDetailState {
    const [state, setState] = useState<AnalysisDetailState>(() =>
        runId ? initialState : missingRunIdState,
    );

    useEffect(() => {
        if (!runId) {
            return;
        }

        let cancelled = false;

        const load = async (): Promise<void> => {
            try {
                const data = await getAnalysisDetailUseCase.execute(runId);
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
                                : new Error("Failed to load run"),
                    });
                }
            }
        };

        void load();

        return () => {
            cancelled = true;
        };
    }, [runId]);

    return state;
}
