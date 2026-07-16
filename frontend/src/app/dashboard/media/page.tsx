"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MediaLibrary } from "@/components/media/media-library"

export default function MediaPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <MediaLibrary />
      </div>
    </DashboardLayout>
  )
}
