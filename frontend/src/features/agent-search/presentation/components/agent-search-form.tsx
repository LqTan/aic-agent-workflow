"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { FormEvent, useState } from "react";

interface AgentSearchFormProps {
    isLoading: boolean;
    onSearch: (query: string, topK: number) => Promise<void>;
}

export function AgentSearchForm({
    isLoading,
    onSearch,
}: AgentSearchFormProps) {
    const [query, setQuery] = useState("");
    const [topK, setTopK] = useState(6);

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const normalized = query.trim();
        if (!normalized || isLoading) return;
        await onSearch(normalized, topK);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Mô tả cảnh bạn muốn tìm, ví dụ: một người đang đi xe đạp ngoài đường..."
                disabled={isLoading}
                rows={3}
            />
            <div className="flex flex-wrap items-center gap-4">
                <label className="flex items-center gap-2 text-sm text-muted-foreground">
                    Top-K
                    <input
                        type="number"
                        min={1}
                        max={20}
                        value={topK}
                        onChange={(event) =>
                            setTopK(Math.max(1, Number(event.target.value) || 1))
                        }
                        disabled={isLoading}
                        className="w-20 rounded-md border border-input bg-background px-2 py-1 text-sm"
                    />
                </label>
                <Button
                    type="submit"
                    disabled={!query.trim() || isLoading}
                >
                    {isLoading ? "Đang gọi n8n..." : "Chạy qua n8n"}
                </Button>
            </div>
        </form>
    );
}