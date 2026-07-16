"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { RepurposeEngine } from "@/components/repurpose/repurpose-engine"

export default function RepurposePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <RepurposeEngine />
      </div>
    </DashboardLayout>
  )
}
