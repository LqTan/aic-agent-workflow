"use client";

import { cn } from "cn";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Activity,
    BarChart3,
    History,
    LayoutDashboard,
    Search,
} from "lucide-react";

interface NavItem {
    href: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    description?: string;
}

const navItems: NavItem[] = [
    {
        href: "/",
        label: "Dashboard",
        icon: LayoutDashboard,
        description: "System overview",
    },
    {
        href: "/search",
        label: "Video Search",
        icon: Search,
        description: "AI Agent search",
    },
    {
        href: "/analysis",
        label: "Analysis",
        icon: Activity,
        description: "Inspect each run",
    },
    {
        href: "/history",
        label: "History",
        icon: History,
        description: "Query timeline",
    },
    {
        href: "/evaluation",
        label: "Evaluation",
        icon: BarChart3,
        description: "Retrieval metrics",
    },
];

interface SidebarNavProps {
    className?: string;
}

export function SidebarNav({ className }: SidebarNavProps) {
    const pathname = usePathname();

    return (
        <aside
            className={cn(
                "flex h-full w-64 shrink-0 flex-col border-r bg-sidebar text-sidebar-foreground",
                className,
            )}
        >
            <div className="border-b px-6 py-6">
                <Link href="/" className="block">
                    <p className="text-lg font-bold tracking-tight">AIC</p>
                    <p className="text-xs text-muted-foreground">
                        Agentic Video Retrieval
                    </p>
                </Link>
            </div>

            <nav className="flex-1 overflow-y-auto px-3 py-6">
                <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Workspace
                </p>
                <ul className="space-y-1">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive =
                            item.href === "/"
                                ? pathname === "/"
                                : pathname === item.href ||
                                  pathname.startsWith(`${item.href}/`);

                        return (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    className={cn(
                                        "flex items-start gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                                        isActive
                                            ? "bg-sidebar-accent text-sidebar-accent-foreground"
                                            : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
                                    )}
                                >
                                    <Icon
                                        className={cn(
                                            "mt-0.5 size-4 shrink-0",
                                            isActive
                                                ? "text-foreground"
                                                : "text-muted-foreground",
                                        )}
                                    />
                                    <span className="flex flex-col gap-0.5">
                                        <span className="font-medium">
                                            {item.label}
                                        </span>
                                        {item.description && (
                                            <span className="text-[11px] text-muted-foreground">
                                                {item.description}
                                            </span>
                                        )}
                                    </span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            <div className="border-t px-6 py-4 text-xs text-muted-foreground">
                <p className="font-semibold text-foreground">AIC Workspace</p>
                <p className="mt-0.5">v0.1 · mock data</p>
            </div>
        </aside>
    );
}
