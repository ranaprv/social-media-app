import NextAuth, { AuthOptions } from "next-auth"
import Google from "next-auth/providers/google"
import GitHub from "next-auth/providers/github"
import Credentials from "next-auth/providers/credentials"

// Server-side: use Docker service name (AUTH_API_URL) if available, fallback to NEXT_PUBLIC
const SERVER_API_URL = process.env.AUTH_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"
// Client-side: use NEXT_PUBLIC_API_URL
const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export const authOptions: AuthOptions = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
    }),
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null

        try {
          const res = await fetch(`${SERVER_API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (!res.ok) {
            console.error("[Auth] Login failed:", res.status, await res.text().catch(() => ""))
            return null
          }

          const data = await res.json()
          return {
            id: data.user_id || "user-1",
            email: credentials.email as string,
            name: data.name || credentials.email as string,
            accessToken: data.access_token,
          }
        } catch (error) {
          console.error("[Auth] Backend unreachable:", SERVER_API_URL, error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.accessToken = (user as Record<string, unknown>)?.accessToken as string ?? ""
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        ;(session.user as Record<string, unknown>).id = token.id as string
        ;(session as Record<string, unknown>).accessToken = token.accessToken
      }
      return session
    },
  },
  pages: {
    signIn: "/auth/login",
    newUser: "/auth/register",
  },
  session: {
    strategy: "jwt",
  },
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
