from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import (
    auth, workspaces, posts, dashboard, connections,
    ai_content, ai_ideas, ai_writing_tools, ai_brand_voice,
    repurpose, calendar, scheduler_api, team, media,
    analytics, billing, security_api, recommendations, ai_media,
)

settings = get_settings()

app = FastAPI(
    title="ContentPilot API",
    description="AI-Powered Social Media Content Management Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "contentpilot-api"}
