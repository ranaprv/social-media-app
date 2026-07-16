const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export async function apiFetch(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  }

  // Try to get access token from NextAuth session via a cookie fetch
  // NextAuth stores the session in a JWT cookie; we can't read it directly,
  // but we can use the session token from a session callback or fetch /api/auth/session
  try {
    const sessionRes = await fetch("/api/auth/session")
    const session = await sessionRes.json()
    const token = session?.accessToken
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }
  } catch {
    // Not logged in or session not available — proceed without token
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `API error: ${res.status}`)
  }

  if (res.status === 204) return null
  return res.json()
}

export { API_URL }
