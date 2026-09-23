"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { FormEvent, useState } from "react";

interface VideoSearchFormProps {
    isLoading: boolean;
    onSearch: (query: string) => Promise<void>;
    useReal: boolean;
    onToggleReal: (next: boolean) => void;
}

export function VideoSearchForm({
    isLoading,
    onSearch,
    useReal,
    onToggleReal,
}: VideoSearchFormProps) {
    const [query, setQuery] = useState("");
    const handleSubmit = async (
        event: FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();
        const normalizedQuery = query.trim();

        if (!normalizedQuery || isLoading) {
            return;
        }
        await onSearch(normalizedQuery);
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="space-y-4"
        >
            <Textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Mô tả nội dung video bạn muốn tìm..."
                disabled={isLoading}
                rows={4}
            />
            <div className="flex flex-wrap items-center justify-between gap-3">
                <Button
                    type="submit"
                    disabled={!query.trim() || isLoading}
                >
                    {isLoading ? "Đang tìm kiếm..." : "Tìm kiếm"}
                </Button>
                <label className="flex cursor-pointer items-center gap-2 rounded-md border bg-muted/30 px-3 py-1.5 text-sm">
                    <input
                        type="checkbox"
                        className="h-4 w-4 cursor-pointer accent-primary"
                        checked={useReal}
                        onChange={(event) => onToggleReal(event.target.checked)}
                        disabled={isLoading}
                    />
                    <span>
                        Dùng data thật từ máy local
                        <span className="ml-1 text-xs text-muted-foreground">
                            (cần bật clip-search-backend.exe)
                        </span>
                    </span>
                </label>
            </div>
        </form>
    );
}
