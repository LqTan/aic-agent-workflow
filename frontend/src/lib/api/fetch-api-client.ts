import { env } from "@/config/env";
import { ApiError } from "./api-error";
import { ApiClient } from "./abstractions/api-client.interface";

export class FetchApiClient implements ApiClient {

    async request<TResponse>(
        path: string,
        options: RequestInit = {},
    ): Promise<TResponse> {
        const url = this.buildUrl(path);

        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
        });

        if (!response.ok) {
            const details = await this.tryReadError(response);

            throw new ApiError(
                response.status,
                `Request failed with status ${response.status}`,
                details,
            );
        }

        return response.json() as Promise<TResponse>;
    }

    private buildUrl(path: string): string {
        const baseUrl = env.apiBaseUrl.replace(/\/$/,"");
        const normalizePath = path.startsWith("/")
            ? path
            : `/${path}`;
        return `${baseUrl}${normalizePath}`;
    }

    private async tryReadError(
        response: Response,
    ): Promise<unknown> {
        try {
            return await response.json();
        } catch {
            return undefined;
        }
    }
}
