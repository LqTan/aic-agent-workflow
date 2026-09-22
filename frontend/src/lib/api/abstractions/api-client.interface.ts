export interface ApiClient {
    request<TResponse>(
        path: string,
        options?: RequestInit,
    ): Promise<TResponse>;
}
