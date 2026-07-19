"""Content template library — save + reuse post templates.

Allows users to save successful posts as templates and reuse them
with different content.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)

# Built-in template categories
BUILTIN_TEMPLATES = [
    {
        "id": "tmpl-1",
        "name": "Product Announcement",
        "category": "announcement",
        "platforms": ["linkedin", "x", "facebook"],
        "content_template": "🚀 Exciting news! {title}\n\n{content}\n\n{cta}",
        "variables": ["title", "content", "cta"],
    },
    {
        "id": "tmpl-2",
        "name": "How-To Tutorial",
        "category": "educational",
        "platforms": ["linkedin", "instagram"],
        "content_template": "📝 How to {topic}:\n\n{step_1}\n{step_2}\n{step_3}\n\n{summary}",
        "variables": ["topic", "step_1", "step_2", "step_3", "summary"],
    },
    {
        "id": "tmpl-3",
        "name": "Weekly Thread",
        "category": "recurring",
        "platforms": ["x"],
        "content_template": "🧵 Thread: {topic}\n\n1/ {point_1}\n2/ {point_2}\n3/ {point_3}\n\nWhat do you think? 👇",
        "variables": ["topic", "point_1", "point_2", "point_3"],
    },
    {
        "id": "tmpl-4",
        "name": "Behind the Scenes",
        "category": "engagement",
        "platforms": ["instagram", "facebook"],
        "content_template": "👀 Behind the scenes of {process}\n\n{description}\n\n{question}",
        "variables": ["process", "description", "question"],
    },
    {
        "id": "tmpl-5",
        "name": "Case Study",
        "category": "social_proof",
        "platforms": ["linkedin", "facebook"],
        "content_template": "📊 Case Study: {client}\n\nChallenge: {challenge}\nSolution: {solution}\nResult: {result}\n\n{cta}",
        "variables": ["client", "challenge", "solution", "result", "cta"],
    },
]


async def get_templates(
    db: AsyncSession,
    workspace_id: str,
    category: str | None = None,
    platform: str | None = None,
) -> list[dict[str, Any]]:
    """Get all templates (built-in + user-saved)."""
    templates = list(BUILTIN_TEMPLATES)

    # Get user-saved templates from Post meta
    query = select(Post).where(
        Post.workspace_id == workspace_id,
        Post.meta["is_template"].as_bool() == True,
    )
    if platform:
        query = query.where(Post.platform == platform)

    result = await db.execute(query.limit(50))
    user_posts = result.scalars().all()

    for post in user_posts:
        meta = post.meta or {}
        templates.append({
            "id": f"custom-{post.id}",
            "name": meta.get("template_name", post.title or "Untitled"),
            "category": meta.get("template_category", "custom"),
            "platforms": [post.platform],
            "content_template": post.content,
            "variables": meta.get("template_variables", []),
            "is_custom": True,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        })

    # Filter
    if category:
        templates = [t for t in templates if t.get("category") == category]
    if platform:
        templates = [t for t in templates if platform in t.get("platforms", [])]

    return templates


async def save_as_template(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    template_name: str,
    template_category: str = "custom",
    variables: list[str] | None = None,
) -> dict[str, Any]:
    """Save an existing post as a reusable template."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    meta = post.meta or {}
    meta["is_template"] = True
    meta["template_name"] = template_name
    meta["template_category"] = template_category
    meta["template_variables"] = variables or []
    meta["saved_at"] = datetime.utcnow().isoformat()
    post.meta = meta

    await db.flush()

    return {
        "template_id": f"custom-{post_id}",
        "name": template_name,
        "category": template_category,
        "content_preview": post.content[:100],
    }


async def create_from_template(
    db: AsyncSession,
    workspace_id: str,
    template_id: str,
    variables: dict[str, str],
    platforms: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new post from a template, filling in variables."""
    # Find the template
    content_template = None
    template_name = ""

    if template_id.startswith("custom-"):
        post_id = template_id.replace("custom-", "")
        result = await db.execute(
            select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
        )
        post = result.scalar_one_none()
        if post:
            content_template = post.content
            template_name = (post.meta or {}).get("template_name", "")
    else:
        for tmpl in BUILTIN_TEMPLATES:
            if tmpl["id"] == template_id:
                content_template = tmpl["content_template"]
                template_name = tmpl["name"]
                break

    if not content_template:
        return {"error": f"Template {template_id} not found"}

    # Fill in variables
    filled_content = content_template
    for key, value in variables.items():
        filled_content = filled_content.replace(f"{{{key}}}", value)

    target_platforms = platforms or ["linkedin"]

    # Create Post
    post = Post(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        author_id="system",
        title=template_name,
        content=filled_content,
        platform=target_platforms[0],
        status="draft",
        meta={"source": "template", "template_id": template_id},
    )
    db.add(post)

    # Create PostPlatform entries
    for platform in target_platforms:
        pp = PostPlatform(
            id=str(uuid.uuid4()),
            post_id=post.id,
            workspace_id=workspace_id,
            platform=platform,
            status="draft",
        )
        db.add(pp)

    await db.flush()

    return {
        "post_id": post.id,
        "template": template_name,
        "content": filled_content[:200],
        "platforms": target_platforms,
    }
