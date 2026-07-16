import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

describe("Card", () => {
  it("renders card with title", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
        </CardHeader>
        <CardContent>Test content</CardContent>
      </Card>
    )
    expect(screen.getByText("Test Title")).toBeDefined()
    expect(screen.getByText("Test content")).toBeDefined()
  })

  it("renders card without header", () => {
    render(
      <Card>
        <CardContent>Just content</CardContent>
      </Card>
    )
    expect(screen.getByText("Just content")).toBeDefined()
  })
})
