"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CalendarViewComponent } from "@/components/calendar/calendar-view"

export default function CalendarPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <CalendarViewComponent />
      </div>
    </DashboardLayout>
  )
}
