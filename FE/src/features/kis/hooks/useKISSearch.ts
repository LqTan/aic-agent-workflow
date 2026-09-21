import { useState } from "react";

import { searchKISAgent } from "../services/kisApi";

import type {KISAgentSearchRequest,KISAgentSearchResponse,} from "../types/kis";

export function useKISSearch() {
    const [data, setData] = useState<KISAgentSearchResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function search(request: KISAgentSearchRequest) {
        setLoading(true);
        setError(null);

        try {
            const response = await searchKISAgent(request);
            setData(response);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "KIS search failed",
            );
        } finally {
            setLoading(false);
        }
    }

    return {
        data,
        loading,
        error,
        search,
    };
}  
