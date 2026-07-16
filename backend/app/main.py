from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import get_settings
from app.middleware.logging import log_requests
from app.api import (
    auth, workspaces, posts, dashboard, connections,
    ai_content, ai_ideas, ai_writing_tools, ai_brand_voice,
    repurpose, calendar, scheduler_api, team, media,
    analytics, billing, security_api, recommendations, ai_media,
    webhooks, research, bulk_scheduler, inbox, listening,
)

settings = get_settings()

app = FastAPI(
    title="Social Media Manager API",
    description="AI-Powered Social Media Content Management Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com"
    return response


# Request logging middleware
@app.middleware("http")
async def request_logging(request: Request, call_next):
    return await log_requests(request, call_next)


# Routes
app.include_router(auth.router, prefix="/api")
app.include_router(workspaces.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(connections.router, prefix="/api")
app.include_router(ai_content.router, prefix="/api")
app.include_router(ai_ideas.router, prefix="/api")
app.include_router(ai_writing_tools.router, prefix="/api")
app.include_router(ai_brand_voice.router, prefix="/api")
app.include_router(repurpose.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")
app.include_router(scheduler_api.router, prefix="/api")
app.include_router(team.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(security_api.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(ai_media.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(bulk_scheduler.router, prefix="/api")
app.include_router(inbox.router, prefix="/api")
app.include_router(listening.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "social-media-manager-api"}
