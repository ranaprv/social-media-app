"""Seed database with demo data."""
import asyncio
import uuid
from datetime import datetime, timedelta
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.content import Post, AnalyticsMetric, BrandVoice


async def seed():
    async with AsyncSessionLocal() as db:
        # Create demo user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email="admin@socialmediamanager.ai",
            name="Admin User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        db.add(user)

        # Create workspace
        workspace_id = str(uuid.uuid4())
        workspace = Workspace(
            id=workspace_id,
            name="Social Media Manager Team",
            slug="social-media-manager-team",
            owner_id=user_id,
        )
        db.add(workspace)

        # Add user as owner
        member = WorkspaceMember(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            role="owner",
        )
        db.add(member)

        # Create demo posts
        platforms = ["linkedin", "x", "instagram", "facebook", "youtube"]
        statuses = ["published", "scheduled", "draft", "review", "published"]
        titles = [
            "10 Tips for Building a SaaS Product",
            "How I Grew My Following to 50K",
            "Behind the Scenes: Our Product Launch",
            "DevOps Best Practices for Startups",
            "Content Strategy Guide 2026",
        ]

        post_ids = []
        for i in range(5):
            post_id = str(uuid.uuid4())
            post_ids.append(post_id)
            post = Post(
                id=post_id,
                workspace_id=workspace_id,
                author_id=user_id,
                title=titles[i],
                content=f"Demo content for {titles[i]}. This is a sample post created during seeding.",
                platform=platforms[i],
                status=statuses[i],
                scheduled_at=datetime.utcnow() + timedelta(days=i) if statuses[i] == "scheduled" else None,
                published_at=datetime.utcnow() - timedelta(days=5 - i) if statuses[i] == "published" else None,
            )
            db.add(post)

        # Create analytics for published posts
        for i, post_id in enumerate(post_ids[:3]):
            metric = AnalyticsMetric(
                id=str(uuid.uuid4()),
                post_id=post_id,
                platform=platforms[i],
                impressions=10000 + i * 5000,
                reach=5000 + i * 2000,
                engagement=500 + i * 200,
                likes=300 + i * 100,
                comments=50 + i * 20,
                shares=30 + i * 15,
                clicks=100 + i * 40,
            )
            db.add(metric)

        # Create brand voice
        brand_voice = BrandVoice(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            tone="Professional yet approachable",
            writing_style="Conversational with industry expertise",
            cta_style="Direct and action-oriented",
            emoji_usage="Minimal, strategic use",
            formatting="Short paragraphs, bullet points",
            vocabulary="Industry-standard with accessible explanations",
        )
        db.add(brand_voice)

        await db.commit()
        print(f"Seeded: 1 user ({user.email}), 1 workspace, 5 posts, 3 analytics, 1 brand voice")


if __name__ == "__main__":
    asyncio.run(seed())
