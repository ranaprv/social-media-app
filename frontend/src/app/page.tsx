import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Zap, ArrowRight, Calendar, BarChart3, PenTool, Repeat } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <Zap className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Social Media Manager</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/auth/login">
              <Button variant="ghost">Log in</Button>
            </Link>
            <Link href="/auth/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="container mx-auto px-4 py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
          AI-Powered Content
          <br />
          <span className="text-primary">Operating System</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
          Research, ideate, create, repurpose, schedule, and publish content
          across YouTube, Instagram, Facebook, LinkedIn, and X from one platform.
          Reduce content creation time by 80%.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link href="/auth/register">
            <Button size="lg" className="gap-2">
              Start Free Trial
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/auth/login">
            <Button size="lg" variant="outline">
              Watch Demo
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-24">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything you need to dominate social media
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: PenTool,
              title: "AI Content Creation",
              description:
                "Generate platform-specific content with AI. Posts, threads, carousels, scripts — all tailored to each platform.",
            },
            {
              icon: Calendar,
              title: "Smart Scheduling",
              description:
                "Schedule posts across 5 platforms. AI suggests best posting times. Drag-and-drop calendar view.",
            },
            {
              icon: Repeat,
              title: "Content Repurposing",
              description:
                "Turn one piece of content into 10. Blog → LinkedIn post → Twitter thread → Instagram caption.",
            },
            {
              icon: BarChart3,
              title: "Analytics & Insights",
              description:
                "Track performance across all platforms. AI recommends improvements for better engagement.",
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border bg-card p-6 transition-all hover:shadow-lg"
            >
              <feature.icon className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="rounded-2xl bg-primary p-12 text-primary-foreground">
          <h2 className="text-3xl font-bold mb-4">
            Ready to transform your content workflow?
          </h2>
          <p className="mb-8 text-lg opacity-90">
            Join thousands of creators, founders, and agencies already using
            Social Media Manager.
          </p>
          <Link href="/auth/register">
            <Button
              size="lg"
              variant="secondary"
              className="gap-2"
            >
              Start Free Trial
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          © 2026 Social Media Manager. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
