const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const useMocks =
    process.env.NEXT_PUBLIC_USE_MOCKS === "true" || !apiBaseUrl;

export const env = {
    apiBaseUrl,
    useMocks,
} as const;
