"use client"

import { Sidebar } from "./sidebar"
import { Header } from "./header"
import { AuthGuard } from "@/components/providers/auth-guard"
import { useAppStore } from "@/stores/app-store"
import { cn } from "@/lib/utils"

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useAppStore()

  return (
    <AuthGuard>
      <div className="min-h-screen bg-background">
        <Sidebar />
        <div
          className={cn(
            "transition-all duration-300",
            sidebarOpen ? "ml-64" : "ml-16"
          )}
        >
          <Header />
          <main className="p-6">{children}</main>
        </div>
      </div>
    </AuthGuard>
  )
}
