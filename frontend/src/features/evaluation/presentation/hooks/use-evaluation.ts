"use client";

import { useEffect, useState } from "react";
import { EvaluationOverview } from "../../domain/models/evaluation.model";
import { getEvaluationOverviewUseCase } from "../../dependency-injection";

interface EvaluationState {
    data: EvaluationOverview | null;
    isLoading: boolean;
    error: Error | null;
}

const initialState: EvaluationState = {
    data: null,
    isLoading: true,
    error: null,
};

export function useEvaluationOverview(): EvaluationState {
    const [state, setState] = useState<EvaluationState>(initialState);

    useEffect(() => {
        let cancelled = false;

        const load = async (): Promise<void> => {
            try {
                const data = await getEvaluationOverviewUseCase.execute();
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
                                : new Error("Failed to load evaluation"),
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
