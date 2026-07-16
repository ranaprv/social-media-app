"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { User, Bell, Palette, Shield } from "lucide-react"

const TABS = [
  { id: "general", label: "General", icon: User },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "security", label: "Security", icon: Shield },
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("general")

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences.
          </p>
        </div>

        {/* Tab buttons */}
        <div className="flex gap-2">
          {TABS.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "bg-card text-muted-foreground hover:bg-muted border"
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Tab content */}
        <Card>
          <CardHeader>
            <CardTitle>{TABS.find((t) => t.id === activeTab)?.label} Settings</CardTitle>
            <CardDescription>
              {activeTab === "general" && "Update your profile information and preferences."}
              {activeTab === "notifications" && "Choose how and when you want to be notified."}
              {activeTab === "appearance" && "Customize the look and feel of your dashboard."}
              {activeTab === "security" && "Manage your password, MFA, and session settings."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {activeTab === "general" && "General settings coming soon. Configure your display name, email, and timezone here."}
              {activeTab === "notifications" && "Notification settings coming soon. Manage email alerts, in-app notifications, and digest preferences."}
              {activeTab === "appearance" && "Theme settings are available in the header theme toggle. More customization options coming soon."}
              {activeTab === "security" && "Security settings coming soon. Configure MFA, manage active sessions, and update your password here."}
            </p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
