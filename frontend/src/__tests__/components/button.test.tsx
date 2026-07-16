import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { Button } from "@/components/ui/button"

describe("Button", () => {
  it("renders children text", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText("Click me")).toBeDefined()
  })

  it("renders with default variant", () => {
    render(<Button>Test</Button>)
    const button = screen.getByRole("button")
    expect(button).toBeDefined()
  })

  it("renders as disabled", () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole("button") as HTMLButtonElement
    expect(button.disabled).toBe(true)
  })

  it("calls onClick handler", () => {
    let clicked = false
    render(<Button onClick={() => (clicked = true)}>Click</Button>)
    screen.getByRole("button").click()
    expect(clicked).toBe(true)
  })
})
