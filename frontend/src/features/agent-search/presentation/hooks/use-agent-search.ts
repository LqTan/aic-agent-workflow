"use client";

import { useState } from "react";
import type {
    AgentSearchRequest,
    AgentSearchResponse,
} from "../../domain/models/agent-search.model";
import { runAgentSearchUseCase } from "../../dependency-injection";

export function useAgentSearch() {
    const [data, setData] = useState<AgentSearchResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [lastDurationMs, setLastDurationMs] = useState<number | null>(null);

    const search = async (request: AgentSearchRequest): Promise<void> => {
        try {
            setIsLoading(true);
            setError(null);
            setData(null);
            const startedAt = performance.now();
            const result = await runAgentSearchUseCase.execute(request);
            setLastDurationMs(Math.round(performance.now() - startedAt));
            setData(result);
        } catch (caught) {
            setLastDurationMs(null);
            setError(
                caught instanceof Error ? caught : new Error("Unexpected error"),
            );
        } finally {
            setIsLoading(false);
        }
    };

    const reset = (): void => {
        setData(null);
        setError(null);
        setLastDurationMs(null);
    };

    return { data, isLoading, error, search, reset, lastDurationMs };
}