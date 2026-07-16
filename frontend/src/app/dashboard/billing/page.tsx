"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  CreditCard,
  CheckCircle,
  ArrowUpRight,
  Download,
  Receipt,
  Shield,
  AlertCircle,
  Loader2,
  Sparkles,
  Zap,
  Star,
  Crown,
  Building2,
  RefreshCw,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const planIcons: Record<string, typeof Star> = {
  free: Zap,
  pro: Star,
  business: Crown,
  enterprise: Building2,
}

const planColors: Record<string, string> = {
  free: "border-gray-200 dark:border-gray-700",
  pro: "border-blue-500 ring-2 ring-blue-500/20",
  business: "border-purple-500 ring-2 ring-purple-500/20",
  enterprise: "border-amber-500 ring-2 ring-amber-500/20",
}

const planBadgeColors: Record<string, string> = {
  free: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
  pro: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  business: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
  enterprise: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
}

const fallbackPlans = [
  {
    id: "free",
    name: "Free",
    price: 0,
    interval: "month",
    credits: 50,
    features: ["50 AI credits/month", "3 platform connections", "Basic analytics", "1 workspace", "Email support"],
    limits: { ai_credits: 50, platforms: 3, workspaces: 1, team_members: 1, media_storage_mb: 100, scheduled_posts: 10 },
  },
  {
    id: "pro",
    name: "Pro",
    price: 29,
    interval: "month",
    credits: 500,
    features: ["500 AI credits/month", "All platform connections", "Advanced analytics", "5 workspaces", "Priority support", "Brand voice training", "Content calendar", "AI repurposing"],
    limits: { ai_credits: 500, platforms: 5, workspaces: 5, team_members: 5, media_storage_mb: 5000, scheduled_posts: 100 },
  },
  {
    id: "business",
    name: "Business",
    price: 99,
    interval: "month",
    credits: 2000,
    features: ["2,000 AI credits/month", "All platform connections", "Full analytics suite", "Unlimited workspaces", "Dedicated support", "Brand voice training", "Content calendar", "AI repurposing", "Team collaboration", "Media library", "Custom integrations"],
    limits: { ai_credits: 2000, platforms: 5, workspaces: -1, team_members: 20, media_storage_mb: 50000, scheduled_posts: -1 },
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: 299,
    interval: "month",
    credits: -1,
    features: ["Unlimited AI credits", "All platform connections", "Enterprise analytics", "Unlimited workspaces", "Dedicated account manager", "Brand voice training", "Content calendar", "AI repurposing", "Team collaboration", "Media library", "Custom integrations", "SSO & SAML", "SLA guarantee", "Custom AI models", "API access"],
    limits: { ai_credits: -1, platforms: -1, workspaces: -1, team_members: -1, media_storage_mb: -1, scheduled_posts: -1 },
  },
]

const fallbackSubscription = {
  plan: "pro",
  status: "active",
  current_period_start: new Date(Date.now() - 15 * 86400000).toISOString(),
  current_period_end: new Date(Date.now() + 15 * 86400000).toISOString(),
  cancel_at_period_end: false,
  payment_method: { brand: "visa", last4: "4242", exp_month: 12, exp_year: 2027 },
}

const fallbackUsage = {
  credits: { used: 312, limit: 500, reset_date: new Date(Date.now() + 15 * 86400000).toISOString().slice(0, 10) },
  workspaces: { used: 3, limit: 5 },
  team_members: { used: 4, limit: 5 },
  media_storage: { used_mb: 2340, limit_mb: 5000 },
  scheduled_posts: { used: 23, limit: 100 },
  platforms_connected: { used: 3, limit: 5 },
}

const fallbackInvoices = [
  { id: "inv-1", date: "2026-07-01", amount: 29, status: "paid", plan: "Pro", description: "Pro Plan — Monthly" },
  { id: "inv-2", date: "2026-06-01", amount: 29, status: "paid", plan: "Pro", description: "Pro Plan — Monthly" },
  { id: "inv-3", date: "2026-05-01", amount: 29, status: "paid", plan: "Pro", description: "Pro Plan — Monthly" },
  { id: "inv-4", date: "2026-04-01", amount: 0, status: "paid", plan: "Free", description: "Free Plan" },
  { id: "inv-5", date: "2026-03-01", amount: 0, status: "paid", plan: "Free", description: "Free Plan" },
]

function UsageBar({ label, used, limit, unit = "" }: { label: string; used: number; limit: number; unit?: string }) {
  const pct = limit === -1 ? 0 : Math.min((used / limit) * 100, 100)
  const color = pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500"
  const isUnlimited = limit === -1

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">
          {isUnlimited ? "Unlimited" : `${used.toLocaleString()} / ${limit.toLocaleString()}${unit}`}
        </span>
      </div>
      {!isUnlimited && (
        <div className="h-2 rounded-full bg-muted">
          <div
            className={`h-2 rounded-full transition-all ${color}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      {isUnlimited && (
        <div className="h-2 rounded-full bg-muted">
          <div className="h-2 w-full rounded-full bg-green-500" />
        </div>
      )}
    </div>
  )
}

export default function BillingPage() {
  const [plans, setPlans] = useState(fallbackPlans)
  const [subscription, setSubscription] = useState(fallbackSubscription)
  const [usage, setUsage] = useState(fallbackUsage)
  const [invoices, setInvoices] = useState(fallbackInvoices)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState<string | null>(null)

  useEffect(() => {
    async function fetchBilling() {
      try {
        const [plansRes, subRes, usageRes, invRes] = await Promise.allSettled([
          fetch(`${API_URL}/billing/plans`),
          fetch(`${API_URL}/billing/subscription`),
          fetch(`${API_URL}/billing/usage`),
          fetch(`${API_URL}/billing/invoices`),
        ])
        if (plansRes.status === "fulfilled" && plansRes.value.ok) {
          const data = await plansRes.value.json()
          if (data.plans) setPlans(data.plans)
        }
        if (subRes.status === "fulfilled" && subRes.value.ok) {
          const data = await subRes.value.json()
          setSubscription(data)
        }
        if (usageRes.status === "fulfilled" && usageRes.value.ok) {
          const data = await usageRes.value.json()
          setUsage(data)
        }
        if (invRes.status === "fulfilled" && invRes.value.ok) {
          const data = await invRes.value.json()
          if (data.invoices) setInvoices(data.invoices)
        }
      } catch {
        // use fallback
      } finally {
        setLoading(false)
      }
    }
    fetchBilling()
  }, [])

  async function handleCheckout(planId: string) {
    setUpgrading(planId)
    try {
      const res = await fetch(`${API_URL}/billing/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan: planId }),
      })
      const data = await res.json()
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    } catch {
      // ignore
    } finally {
      setUpgrading(null)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Billing & Subscription</h1>
            <p className="text-muted-foreground">Manage your plan, usage, and payment details.</p>
          </div>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => window.location.reload()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>

        {/* Current Plan + Usage */}
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-primary" />
                Current Plan
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold capitalize">{subscription.plan}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    subscription.status === "active"
                      ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                  }`}>
                    {subscription.status}
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  {subscription.cancel_at_period_end ? "Cancels" : "Renews"} on{" "}
                  {new Date(subscription.current_period_end).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
                </p>
              </div>
              <div className="rounded-lg border p-3">
                <div className="flex items-center gap-2 text-sm">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium capitalize">{subscription.payment_method.brand}</span>
                  <span className="text-muted-foreground">•••• {subscription.payment_method.last4}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  Expires {subscription.payment_method.exp_month}/{subscription.payment_method.exp_year}
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1">
                  Update Payment
                </Button>
                {!subscription.cancel_at_period_end && subscription.plan !== "free" && (
                  <Button variant="destructive" size="sm" className="flex-1">
                    Cancel
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Usage This Period</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <UsageBar label="AI Credits" used={usage.credits.used} limit={usage.credits.limit} />
              <UsageBar label="Workspaces" used={usage.workspaces.used} limit={usage.workspaces.limit} />
              <UsageBar label="Team Members" used={usage.team_members.used} limit={usage.team_members.limit} />
              <UsageBar label="Media Storage" used={usage.media_storage.used_mb} limit={usage.media_storage.limit_mb} unit=" MB" />
              <UsageBar label="Scheduled Posts" used={usage.scheduled_posts.used} limit={usage.scheduled_posts.limit} />
              <UsageBar label="Platforms Connected" used={usage.platforms_connected.used} limit={usage.platforms_connected.limit} />
            </CardContent>
          </Card>
        </div>

        {/* Plan Cards */}
        <div>
          <h2 className="mb-4 text-xl font-semibold">Subscription Plans</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {plans.map((plan) => {
              const Icon = planIcons[plan.id] || Star
              const isCurrent = plan.id === subscription.plan
              return (
                <Card
                  key={plan.id}
                  className={`relative flex flex-col ${planColors[plan.id] || ""} ${isCurrent ? "shadow-md" : ""}`}
                >
                  {isCurrent && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className={`rounded-full px-3 py-1 text-xs font-medium ${planBadgeColors[plan.id] || ""}`}>
                        Current Plan
                      </span>
                    </div>
                  )}
                  <CardHeader className="text-center">
                    <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{plan.name}</CardTitle>
                    <div>
                      <span className="text-3xl font-bold">{plan.price === 0 ? "Free" : `$${plan.price}`}</span>
                      {plan.price > 0 && <span className="text-muted-foreground">/mo</span>}
                    </div>
                  </CardHeader>
                  <CardContent className="flex flex-1 flex-col">
                    <ul className="mb-6 flex-1 space-y-2">
                      {plan.features.map((feature: string) => (
                        <li key={feature} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-500" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    {isCurrent ? (
                      <Button variant="outline" className="w-full" disabled>
                        Current Plan
                      </Button>
                    ) : plan.id === "enterprise" ? (
                      <Button variant="outline" className="w-full gap-2">
                        <Building2 className="h-4 w-4" />
                        Contact Sales
                      </Button>
                    ) : (
                      <Button
                        className="w-full gap-2"
                        onClick={() => handleCheckout(plan.id)}
                        disabled={upgrading !== null}
                      >
                        {upgrading === plan.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <ArrowUpRight className="h-4 w-4" />
                        )}
                        {plan.price > (plans.find((p) => p.id === subscription.plan)?.price || 0)
                          ? "Upgrade"
                          : "Switch Plan"}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Invoice History */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Receipt className="h-5 w-5" />
                Invoice History
              </CardTitle>
              <Button variant="ghost" size="sm" className="gap-1">
                <Download className="h-4 w-4" />
                Export All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-3 font-medium">Date</th>
                    <th className="pb-3 font-medium">Description</th>
                    <th className="pb-3 font-medium">Amount</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium">Invoice</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map((inv) => (
                    <tr key={inv.id} className="border-b last:border-0">
                      <td className="py-3">
                        {new Date(inv.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                      </td>
                      <td className="py-3">{inv.description}</td>
                      <td className="py-3 font-medium">{inv.amount === 0 ? "—" : `$${inv.amount}.00`}</td>
                      <td className="py-3">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          inv.status === "paid"
                            ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                            : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
                        }`}>
                          {inv.status}
                        </span>
                      </td>
                      <td className="py-3">
                        <Button variant="ghost" size="sm" className="gap-1 h-8">
                          <Download className="h-3 w-3" />
                          PDF
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
