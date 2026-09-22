const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
const useMocks = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

if (!useMocks && !apiBaseUrl) {
    throw new Error(
        "Missing environment variable: NEXT_PUBLIC_API_BASE_URL (or set NEXT_PUBLIC_USE_MOCKS=true)",
    );
}

export const env = {
    apiBaseUrl: apiBaseUrl ?? "",
    useMocks,
} as const;
