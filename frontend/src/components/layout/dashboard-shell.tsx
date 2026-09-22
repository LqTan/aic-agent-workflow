import { SidebarNav } from "./sidebar-nav";

interface DashboardShellProps {
    children: React.ReactNode;
}

export function DashboardShell({ children }: DashboardShellProps) {
    return (
        <div className="flex min-h-screen bg-background text-foreground">
            <SidebarNav className="sticky top-0 h-screen" />

            <div className="flex min-w-0 flex-1 flex-col">
                <main className="flex-1 px-6 py-8 md:px-10">
                    <div className="mx-auto w-full max-w-7xl space-y-8">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
