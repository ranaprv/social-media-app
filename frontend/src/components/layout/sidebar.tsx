"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Calendar,
  PenTool,
  BarChart3,
  Settings,
  Zap,
  Search,
  Repeat,
  Image,
  Video,
  Users,
  Bell,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Lightbulb,
  Wand2,
  CreditCard,
  Shield,
  Mail,
  MessageSquare,
  AlertCircle,
  CheckCircle,
} from "lucide-react"
import { useAppStore } from "@/stores/app-store"
import { Button } from "@/components/ui/button"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Content Studio", href: "/dashboard/content-studio", icon: Sparkles },
  { name: "Research", href: "/dashboard/research", icon: Search },
  { name: "Calendar", href: "/dashboard/calendar", icon: Calendar },
  { name: "Repurpose", href: "/dashboard/repurpose", icon: Repeat },
  { name: "Media", href: "/dashboard/media", icon: Image },
  { name: "Inbox", href: "/dashboard/inbox", icon: Mail },
  { name: "Listening", href: "/dashboard/listening", icon: Search },
  { name: "AI Assistant", href: "/dashboard/ai-assistant", icon: Wand2 },
  { name: "Recommendations", href: "/dashboard/recommendations", icon: Lightbulb },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { name: "Ads", href: "/dashboard/ads", icon: PenTool },
  { name: "Reports", href: "/dashboard/reports", icon: BarChart3 },
  { name: "Competitors", href: "/dashboard/competitors", icon: Users },
  { name: "Team", href: "/dashboard/team", icon: Users },
]

const bottomNavigation = [
  { name: "Approvals", href: "/dashboard/approvals", icon: CheckCircle },
  { name: "Tasks", href: "/dashboard/tasks", icon: AlertCircle },
  { name: "Automation", href: "/dashboard/automation", icon: Zap },
  { name: "Advocacy", href: "/dashboard/advocacy", icon: Users },
  { name: "Billing", href: "/dashboard/billing", icon: CreditCard },
  { name: "Security", href: "/dashboard/security", icon: Shield },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const { sidebarOpen, toggleSidebar } = useAppStore()

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r bg-card transition-all duration-300",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b px-4">
          {sidebarOpen && (
            <Link href="/dashboard" className="flex items-center gap-2">
              <Zap className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">Social Media Manager</span>
            </Link>
          )}
          {!sidebarOpen && (
            <Link href="/dashboard" className="mx-auto">
              <Zap className="h-6 w-6 text-primary" />
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="h-8 w-8"
          >
            {sidebarOpen ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Bottom Navigation */}
        <div className="border-t p-2">
          {bottomNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
