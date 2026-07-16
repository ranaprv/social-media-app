"use client"

import { create } from "zustand"
import { X, CheckCircle, AlertCircle, Info } from "lucide-react"

type ToastType = "success" | "error" | "info"

interface Toast {
  id: string
  type: ToastType
  message: string
}

interface ToastStore {
  toasts: Toast[]
  addToast: (type: ToastType, message: string) => void
  removeToast: (id: string) => void
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (type, message) => {
    const id = Math.random().toString(36).slice(2)
    set((state) => ({ toasts: [...state.toasts, { id, type, message }] }))
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }))
    }, 5000)
  },
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}))

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
}

const colors = {
  success: "border-green-500 bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-400",
  error: "border-red-500 bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-400",
  info: "border-blue-500 bg-blue-50 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400",
}

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore()

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => {
        const Icon = icons[toast.type]
        return (
          <div
            key={toast.id}
            className={`flex items-center gap-3 rounded-lg border p-4 shadow-lg ${colors[toast.type]} min-w-[300px] animate-in slide-in-from-right`}
          >
            <Icon className="h-5 w-5 flex-shrink-0" />
            <span className="flex-1 text-sm">{toast.message}</span>
            <button onClick={() => removeToast(toast.id)} className="flex-shrink-0">
              <X className="h-4 w-4" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
