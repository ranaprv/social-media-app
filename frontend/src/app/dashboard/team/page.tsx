"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { TeamCollaboration } from "@/components/team/team-collaboration"

export default function TeamPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <TeamCollaboration />
      </div>
    </DashboardLayout>
  )
}
