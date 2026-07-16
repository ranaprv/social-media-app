FROM node:20-alpine AS builder
WORKDIR /app

# Build-time env vars (NEXT_PUBLIC_* must be set here for Next.js to inline them)
ARG NEXT_PUBLIC_API_URL=http://localhost:8002/api
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ARG NEXTAUTH_URL=http://localhost:3001
ENV NEXTAUTH_URL=$NEXTAUTH_URL
ARG NEXTAUTH_SECRET=change-this-in-production
ENV NEXTAUTH_SECRET=$NEXTAUTH_SECRET
# Server-side API URL for NextAuth authorize (Docker internal networking)
ARG AUTH_API_URL=http://backend:8000/api
ENV AUTH_API_URL=$AUTH_API_URL

COPY package*.json ./
RUN npm ci
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Runtime env vars
# NEXT_PUBLIC_* = used by browser (needs host-mapped port)
# AUTH_API_URL = used by NextAuth server-side (needs Docker service name)
ENV NEXT_PUBLIC_API_URL=http://localhost:8002/api
ENV AUTH_API_URL=http://backend:8000/api
ENV NEXTAUTH_URL=http://localhost:3001
ENV NEXTAUTH_SECRET=change-this-in-production

RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["npm", "start"]
