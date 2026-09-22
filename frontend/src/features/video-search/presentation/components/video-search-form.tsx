"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { FormEvent, useState } from "react";

interface VideoSearchFormProps {
    isLoading: boolean;
    onSearch: (query: string) => Promise<void>;
}

export function VideoSearchForm({
    isLoading,
    onSearch,
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
            <Button
                type="submit"
                disabled={!query.trim() || isLoading}
            >
                {isLoading ? "Đang tìm kiếm..." : "Tìm kiếm"}
            </Button>
        </form>
    );
}
