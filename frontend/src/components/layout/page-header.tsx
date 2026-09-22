"use client";

import { usePathname } from "next/navigation";

interface PageHeaderProps {
    title: string;
    description?: string;
}

const titles: Record<string, { title: string; description: string }> = {
    "/": {
        title: "Dashboard",
        description: "Tổng quan hệ thống AI Agent",
    },
    "/search": {
        title: "Video Search Agent",
        description: "Tìm kiếm nội dung video bằng ngôn ngữ tự nhiên",
    },
    "/analysis": {
        title: "Analysis",
        description: "Phân tích chi tiết từng lần chạy",
    },
    "/history": {
        title: "Query History",
        description: "Lịch sử truy vấn",
    },
    "/evaluation": {
        title: "Evaluation",
        description: "Đánh giá retrieval và quality scoring",
    },
};

const resolveTitle = (
    pathname: string,
    override?: { title: string; description?: string },
): { title: string; description?: string } => {
    if (override?.title) {
        return override;
    }

    if (pathname.startsWith("/analysis/")) {
        return { title: "Run detail", description: "Phân tích một lần chạy" };
    }

    return (
        titles[pathname] ?? {
            title: override?.title ?? "AIC",
            description: override?.description,
        }
    );
};

export function PageHeader({ title, description }: PageHeaderProps) {
    const pathname = usePathname();
    const resolved = resolveTitle(pathname, { title, description });

    return (
        <div className="space-y-1">
            <h1 className="text-2xl font-bold tracking-tight">
                {resolved.title}
            </h1>
            {resolved.description && (
                <p className="text-sm text-muted-foreground">
                    {resolved.description}
                </p>
            )}
        </div>
    );
}
