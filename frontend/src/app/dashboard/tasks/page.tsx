"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, Plus, CheckCircle, Clock, AlertTriangle, ArrowRight } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface Task { id: string; title: string; description: string; status: string; priority: string; due_date: string | null; created_at: string }

const STATUS_CONFIG: Record<string, { icon: typeof CheckCircle; color: string }> = {
  open: { icon: AlertTriangle, color: "text-orange-500" },
  in_progress: { icon: Clock, color: "text-blue-500" },
  resolved: { icon: CheckCircle, color: "text-green-500" },
}

const PRIORITY_COLORS: Record<string, string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  low: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("")

  useEffect(() => {
    const url = filter ? `${API_URL}/tasks?status=${filter}` : `${API_URL}/tasks`
    fetch(url).then(r => r.json()).then(d => setTasks(d.tasks || [])).catch(() => {}).finally(() => setLoading(false))
  }, [filter])

  const updateStatus = async (id: string, status: string) => {
    await fetch(`${API_URL}/tasks/${id}/status`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) })
    setTasks((p) => p.map((t) => t.id === id ? { ...t, status } : t))
  }

  const openTasks = tasks.filter((t) => t.status === "open")
  const inProgress = tasks.filter((t) => t.status === "in_progress")
  const resolved = tasks.filter((t) => t.status === "resolved")

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Tasks</h1><p className="text-muted-foreground">Track and manage team tasks from inbox messages.</p></div>
        <div className="flex gap-2">
          {["", "open", "in_progress", "resolved"].map((f) => (
            <Button key={f} variant={filter === f ? "default" : "outline"} size="sm" onClick={() => setFilter(f)}>
              {f === "" ? "All" : f === "in_progress" ? "In Progress" : f.charAt(0).toUpperCase() + f.slice(1)}
              {f && <span className="ml-1 text-xs">({tasks.filter((t) => f === "" || t.status === f).length})</span>}
            </Button>
          ))}
        </div>
        {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : (
          <div className="space-y-3">
            {tasks.map((task) => {
              const cfg = STATUS_CONFIG[task.status] || STATUS_CONFIG.open
              const StatusIcon = cfg.icon
              return (
                <Card key={task.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <StatusIcon className={`mt-0.5 h-5 w-5 ${cfg.color}`} />
                        <div>
                          <h4 className="font-medium">{task.title}</h4>
                          <p className="text-sm text-muted-foreground">{task.description}</p>
                          <div className="mt-1 flex items-center gap-2">
                            <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${PRIORITY_COLORS[task.priority]}`}>{task.priority}</span>
                            {task.due_date && <span className="text-xs text-muted-foreground">Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-1">
                        {task.status === "open" && <Button size="sm" variant="outline" onClick={() => updateStatus(task.id, "in_progress")} className="gap-1"><ArrowRight className="h-3 w-3" /> Start</Button>}
                        {task.status === "in_progress" && <Button size="sm" onClick={() => updateStatus(task.id, "resolved")} className="gap-1"><CheckCircle className="h-3 w-3" /> Resolve</Button>}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
