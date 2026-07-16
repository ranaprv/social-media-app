import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { ThemeProvider, useTheme } from "@/components/providers/theme-provider"

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(window, "localStorage", { value: localStorageMock })

// Mock matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  })),
})

function TestComponent() {
  const { theme, resolvedTheme, setTheme } = useTheme()
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <span data-testid="resolved">{resolvedTheme}</span>
      <button onClick={() => setTheme("dark")}>Set Dark</button>
      <button onClick={() => setTheme("light")}>Set Light</button>
    </div>
  )
}

describe("ThemeProvider", () => {
  it("provides default theme", () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )
    expect(screen.getByTestId("theme").textContent).toBe("system")
  })

  it("allows theme changes", () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )
    screen.getByText("Set Dark").click()
    expect(screen.getByTestId("theme").textContent).toBe("dark")
  })

  it("persists to localStorage", () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )
    screen.getByText("Set Light").click()
    expect(localStorageMock.getItem("social-media-manager-theme")).toBe("light")
  })
})
