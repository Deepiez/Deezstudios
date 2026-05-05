"use client";

import { Sidebar } from "./sidebar";
import { AuthGuard } from "./auth-guard";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <main className="pl-64">
          <div className="p-8">{children}</div>
        </main>
      </div>
    </AuthGuard>
  );
}
