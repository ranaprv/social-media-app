"""Research service — business logic for all research endpoints.

Handles LLM calls, response parsing, Video SEO scoring, and DB persistence.
Every LLM response is saved to research_items for later retrieval.
"""
import logging
import uuid
from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.research import ResearchItem
from app.services.llm import call_llm_json
from app.services.video_seo_scorer import (
    compute_video_seo_score,
    compute_thumbnail_ctr_score,
    score_to_tier,
)

logger = logging.getLogger(__name__)


class ResearchService:
    """Orchestrates research workflows: LLM → parse → score → persist."""

    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    # ── Workspace resolution ──────────────────────────────────────────────

    async def _get_workspace_id(self) -> str:
        """Get the first workspace for the current user."""
        result = await self.db.execute(
            select(Workspace.id).where(Workspace.owner_id == self.user.id).limit(1)
        )
        row = result.first()
        if row:
            return row[0]
        raise ValueError("No workspace found for user")

    async def _persist(self, category: str, topic: str, platform: str, data: dict,
                       subcategory: str = None, **extra_fields) -> ResearchItem:
        """Create and persist a research_items row."""
        workspace_id = await self._get_workspace_id()
        item = ResearchItem(
            workspace_id=uuid.UUID(workspace_id) if isinstance(workspace_id, str) else workspace_id,
            category=category,
            subcategory=subcategory,
            topic=topic,
            platform=platform,
            data=data,
            source="llm",
            **extra_fields,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    # ── Keywords ──────────────────────────────────────────────────────────

    async def keyword_research(self, topic: str, platform: str, niche: str,
                                provider: str = "openai", model: str = None) -> dict:
        system_prompt = """You are a Video SEO keyword research expert. Analyze keywords for video content optimization.

Return a JSON object with:
- "keywords": array of {keyword, search_volume: "high"|"medium"|"low", keyword_difficulty: 1-100, competition_level: "low"|"medium"|"high", platform_relevance: {youtube: 1-100, tiktok: 1-100, instagram: 1-100}, content_type: string, why_it_works: string}
- "long_tail_opportunities": array of specific long-tail keywords
- "content_pillar_suggestions": array of content pillar groupings

Return ONLY valid JSON, no markdown."""

        user_prompt = f"""Research Video SEO keywords for: {topic}
Niche: {niche}
Platform focus: {platform}

Identify 8-12 keywords with their Video SEO metrics. Focus on keywords where video content can rank."""

        result = await call_llm_json(user_prompt, system_prompt, provider=provider,
                                     model=model, temperature=0.7, max_tokens=3000)

        if not result:
            result = self._default_keywords(topic, niche)

        # Score and persist each keyword
        keywords = result.get("keywords", [])
        saved_ids = []
        for kw in keywords:
            difficulty = kw.get("keyword_difficulty", 50)
            volume = kw.get("search_volume", "medium")
            competition = kw.get("competition_level", "medium")

            seo_score = compute_video_seo_score(difficulty, volume, competition)
            kw["video_seo_score"] = seo_score
            kw["tier"] = score_to_tier(seo_score)

            item = await self._persist(
                category="keyword",
                topic=kw.get("keyword", topic),
                platform=platform,
                data=kw,
                subcategory="video_seo",
                keyword_difficulty=difficulty,
                search_volume=volume,
                competition_level=competition,
                video_seo_score=seo_score,
                content_pillar=kw.get("content_type"),
            )
            saved_ids.append(str(item.id))

        return {
            "keywords": keywords,
            "long_tail_opportunities": result.get("long_tail_opportunities", []),
            "content_pillar_suggestions": result.get("content_pillar_suggestions", []),
            "saved_ids": saved_ids,
            "count": len(keywords),
        }

    def _default_keywords(self, topic: str, niche: str) -> dict:
        kw = topic or niche
        return {
            "keywords": [
                {"keyword": kw, "search_volume": "high", "keyword_difficulty": 50,
                 "competition_level": "medium", "platform_relevance": {"youtube": 75, "tiktok": 60, "instagram": 55},
                 "content_type": "tutorial", "why_it_works": f"Core keyword for {niche or topic}"},
                {"keyword": f"how to {kw}", "search_volume": "medium", "keyword_difficulty": 30,
                 "competition_level": "low", "platform_relevance": {"youtube": 85, "tiktok": 40, "instagram": 30},
                 "content_type": "tutorial", "why_it_works": "High-intent search query"},
                {"keyword": f"best {kw} tips", "search_volume": "medium", "keyword_difficulty": 40,
                 "competition_level": "medium", "platform_relevance": {"youtube": 70, "tiktok": 65, "instagram": 60},
                 "content_type": "listicle", "why_it_works": "Practical value keyword"},
            ],
            "long_tail_opportunities": [f"best {kw} for beginners", f"{kw} step by step", f"{kw} tutorial 2026"],
            "content_pillar_suggestions": [{"pillar_topic": kw, "cluster_keywords": [f"{kw} guide", f"{kw} tips"]}],
        }

    # ── Competitors ───────────────────────────────────────────────────────

    async def competitor_analysis(self, competitors: list[str], niche: str,
                                   provider: str = "openai", model: str = None) -> dict:
        system_prompt = """You are a competitive intelligence analyst. Analyze competitor content strategies.
Return a JSON object with:
- "competitors": array of {name, strengths, weaknesses, content_strategy, posting_frequency, top_content_types: [], engagement_level: "high"|"medium"|"low", opportunities_to_differentiate}
- "market_gaps": array of content gaps (strings)
- "recommendations": array of actionable recommendations (strings)

Return ONLY valid JSON, no markdown."""

        comp_text = ", ".join(competitors) if competitors else f"Competitors in {niche}"
        user_prompt = f"""Analyze competitors: {comp_text}
Niche: {niche}

Provide comprehensive competitive analysis with actionable recommendations.
Include specific content strategy insights and posting patterns."""

        result = await call_llm_json(user_prompt, system_prompt, provider=provider,
                                     model=model, temperature=0.7, max_tokens=3000)

        if not result:
            result = self._default_competitors(competitors, niche)

        # Persist competitor analysis
        item = await self._persist(
            category="competitor",
            topic=comp_text[:255],
            platform="all",
            data=result,
            subcategory="competitive_analysis",
        )

        return {
            "competitors": result.get("competitors", []),
            "market_gaps": result.get("market_gaps", []),
            "recommendations": result.get("recommendations", []),
            "saved_id": str(item.id),
        }

    def _default_competitors(self, competitors: list[str], niche: str) -> dict:
        names = competitors or ["Competitor 1"]
        return {
            "competitors": [
                {"name": c, "strengths": "Established brand presence",
                 "weaknesses": "Generic content strategy",
                 "content_strategy": "Standard posting cadence",
                 "posting_frequency": "Daily",
                 "top_content_types": ["posts", "stories", "reels"],
                 "engagement_level": "medium",
                 "opportunities_to_differentiate": "Niche down on specific sub-topics"}
                for c in names
            ],
            "market_gaps": [f"Underserved sub-topic in {niche}", "Interactive content missing", "Video tutorial gap"],
            "recommendations": [
                f"Focus on {niche} sub-niches competitors ignore",
                "Create video-first content strategy",
                "Build community-driven engagement",
            ],
        }

    # ── Trends ────────────────────────────────────────────────────────────

    async def trend_analysis(self, topic: str, platform: str,
                              provider: str = "openai", model: str = None) -> dict:
        system_prompt = """You are a trend research analyst. Analyze trending topics for video content.
Return a JSON object with:
- "trends": array of {topic, description, popularity: 1-100, trend_direction: "rising"|"stable"|"declining", velocity: 0.0-1.0, content_opportunity: string, platform_relevance: {youtube: 1-100, tiktok: 1-100, instagram: 1-100}}
- "related_topics": array of related trending topics (strings)
- "best_time_to_post": object with day_of_week and time

Return ONLY valid JSON, no markdown."""

        user_prompt = f"""Research trending topics for: {topic}
Platform focus: {platform}

Identify 5-8 trends with direction tracking (rising/stable/declining), velocity scores, and content opportunities. Focus on video content trends."""

        result = await call_llm_json(user_prompt, system_prompt, provider=provider,
                                     model=model, temperature=0.7, max_tokens=3000)

        if not result:
            result = self._default_trends(topic)

        # Persist each trend
        trends = result.get("trends", [])
        saved_ids = []
        for trend in trends:
            direction = trend.get("trend_direction", "stable")
            velocity = trend.get("velocity", 0.5)

            item = await self._persist(
                category="trend",
                topic=trend.get("topic", topic),
                platform=platform,
                data=trend,
                subcategory="trend_analysis",
                trend_direction=direction,
                trend_velocity=velocity,
            )
            saved_ids.append(str(item.id))

        return {
            "trends": trends,
            "related_topics": result.get("related_topics", []),
            "best_time_to_post": result.get("best_time_to_post", {}),
            "saved_ids": saved_ids,
            "count": len(trends),
        }

    def _default_trends(self, topic: str) -> dict:
        return {
            "trends": [
                {"topic": f"{topic} trends 2026", "description": f"Growing interest in {topic} content",
                 "popularity": 75, "trend_direction": "rising", "velocity": 0.7,
                 "content_opportunity": f"Create timely content around emerging {topic} trends",
                 "platform_relevance": {"youtube": 80, "tiktok": 85, "instagram": 70}},
            ],
            "related_topics": [f"{topic} tips", f"{topic} predictions", f"best {topic} 2026"],
            "best_time_to_post": {"day_of_week": "Tuesday", "time": "10:00 AM"},
        }

    # ── Thumbnails ────────────────────────────────────────────────────────

    async def thumbnail_testing(self, topic: str, platform: str,
                                 provider: str = "openai", model: str = None,
                                 variant_count: int = 4) -> dict:
        system_prompt = """You are a YouTube/thumbnail optimization expert. Generate title and thumbnail variants scored by predicted CTR.
Return a JSON object with:
- "title_variants": array of {title, predicted_ctr: 0.0-1.0, emotional_trigger: string, target_audience: string, thumbnail_concept: string, visual_elements: [], why_it_works: string}
- "thumbnail_concepts": array of {concept_name, description, style: "bold_text"|"face_react"|"curiosity_gap"|"comparison", color_scheme: [], best_for: string}
- "best_practices": array of strings

Return ONLY valid JSON, no markdown."""

        user_prompt = f"""Generate {variant_count} title and thumbnail variants for a video about: {topic}
Platform: {platform}

Create diverse title styles (numbered list, question, how-to, controversy, etc.) with matching thumbnail concepts. Score each by predicted CTR."""

        result = await call_llm_json(user_prompt, system_prompt, provider=provider,
                                     model=model, temperature=0.8, max_tokens=3000)

        if not result:
            result = self._default_thumbnails(topic, variant_count)

        # Score and persist each variant
        titles = result.get("title_variants", [])
        saved_ids = []
        for idx, title_var in enumerate(titles):
            ctr = title_var.get("predicted_ctr", 0.05)
            # Use engagement proxy based on rank position
            engagement = max(0.01, 0.5 - (idx * 0.1))
            seo_score = compute_thumbnail_ctr_score(ctr, engagement)
            title_var["seo_score"] = seo_score
            title_var["tier"] = score_to_tier(seo_score)

            item = await self._persist(
                category="thumbnail",
                topic=title_var.get("title", topic)[:255],
                platform=platform,
                data=title_var,
                subcategory="title_test",
                video_seo_score=seo_score,
                engagement_rate=ctr,
            )
            saved_ids.append(str(item.id))

        return {
            "title_variants": titles,
            "thumbnail_concepts": result.get("thumbnail_concepts", []),
            "best_practices": result.get("best_practices", []),
            "saved_ids": saved_ids,
            "count": len(titles),
        }

    def _default_thumbnails(self, topic: str, count: int) -> dict:
        variants = [
            {"title": f"Top {count} {topic} Tips You NEED to Know",
             "predicted_ctr": 0.08, "emotional_trigger": "urgency",
             "target_audience": "beginners", "thumbnail_concept": "Bold text with numbered list",
             "visual_elements": ["big numbers", "bright colors", "face reaction"],
             "why_it_works": "Numbered lists create curiosity"},
            {"title": f"How I Mastered {topic} in 30 Days",
             "predicted_ctr": 0.06, "emotional_trigger": "aspiration",
             "target_audience": "intermediate", "thumbnail_concept": "Before/after transformation",
             "visual_elements": ["split image", "progress arrow", "surprised face"],
             "why_it_works": "Personal journey stories drive engagement"},
        ]
        concepts = [
            {"concept_name": "Bold Text Overlay", "description": "Large text on contrasting background",
             "style": "bold_text", "color_scheme": ["red", "white", "black"], "best_for": "listicles"},
            {"concept_name": "Face Reaction", "description": "Expressive face with curiosity gap",
             "style": "face_react", "color_scheme": ["bright", "warm tones"], "best_for": "personal stories"},
        ]
        return {
            "title_variants": variants[:count],
            "thumbnail_concepts": concepts,
            "best_practices": ["Use contrasting colors", "Keep text under 5 words", "Show emotion in thumbnails"],
        }

    # ── Audience ──────────────────────────────────────────────────────────

    async def audience_analytics(self, platform: str, niche: str,
                                  provider: str = "openai", model: str = None) -> dict:
        system_prompt = """You are an audience analytics expert. Analyze audience demographics and behavior for video content.
Return a JSON object with:
- "demographics": {age_groups: {group: percentage}, gender_split: {gender: percentage}, top_locations: [string], languages: [string]}
- "peak_engagement": {best_days: [], best_hours: [], timezone_notes: string}
- "content_preferences": {preferred_formats: [], topics_of_interest: [], content_length: string, engagement_triggers: []}
- "audience_insights": array of actionable insights (strings)

Return ONLY valid JSON, no markdown."""

        user_prompt = f"""Analyze the target audience for:
Platform: {platform}
Niche: {niche}

Provide detailed demographics, peak engagement windows, and content preferences. Be specific about timing and format preferences."""

        result = await call_llm_json(user_prompt, system_prompt, provider=provider,
                                     model=model, temperature=0.7, max_tokens=3000)

        if not result:
            result = self._default_audience(platform, niche)

        # Persist audience analysis
        item = await self._persist(
            category="audience",
            topic=f"{niche} audience on {platform}",
            platform=platform,
            data=result,
            subcategory="demographics",
        )

        return {
            "demographics": result.get("demographics", {}),
            "peak_engagement": result.get("peak_engagement", {}),
            "content_preferences": result.get("content_preferences", {}),
            "audience_insights": result.get("audience_insights", []),
            "saved_id": str(item.id),
        }

    def _default_audience(self, platform: str, niche: str) -> dict:
        return {
            "demographics": {
                "age_groups": {"18-24": 25, "25-34": 35, "35-44": 25, "45+": 15},
                "gender_split": {"male": 55, "female": 40, "other": 5},
                "top_locations": ["United States", "United Kingdom", "Canada", "Australia"],
                "languages": ["English"],
            },
            "peak_engagement": {
                "best_days": ["Tuesday", "Thursday", "Saturday"],
                "best_hours": ["9:00 AM", "12:00 PM", "7:00 PM"],
                "timezone_notes": "Optimize for your audience's primary timezone",
            },
            "content_preferences": {
                "preferred_formats": ["short-form video", "tutorials", "behind-the-scenes"],
                "topics_of_interest": [f"{niche} tips", f"best practices", f"trends"],
                "content_length": "7-15 minutes for tutorials, 30-60 seconds for shorts",
                "engagement_triggers": ["questions", "challenges", "controversial takes"],
            },
            "audience_insights": [
                f"Audience on {platform} prefers authentic, unpolished content",
                "Post consistently at peak hours for best engagement",
                "Use calls-to-action to drive comments and shares",
            ],
        }

    # ── Saved items CRUD ──────────────────────────────────────────────────

    async def get_saved(self, category: str = None, platform: str = None,
                        pillar: str = None, limit: int = 20, offset: int = 0) -> dict:
        """Query saved research items with optional filters."""
        workspace_id = await self._get_workspace_id()

        query = select(ResearchItem).where(
            ResearchItem.workspace_id == uuid.UUID(workspace_id)
        )
        count_query = select(func.count(ResearchItem.id)).where(
            ResearchItem.workspace_id == uuid.UUID(workspace_id)
        )

        if category:
            query = query.where(ResearchItem.category == category)
            count_query = count_query.where(ResearchItem.category == category)
        if platform:
            query = query.where(ResearchItem.platform == platform)
            count_query = count_query.where(ResearchItem.platform == platform)
        if pillar:
            query = query.where(ResearchItem.content_pillar == pillar)
            count_query = count_query.where(ResearchItem.content_pillar == pillar)

        # Total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(ResearchItem.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "offset": offset,
            "limit": limit,
        }

    # ── Engine Integration Queries ─────────────────────────────────────────

    async def get_by_pillar(self, pillar_name: str) -> list:
        """Get research items linked to a content pillar. Used by Strategy engine."""
        workspace_id = await self._get_workspace_id()
        query = (
            select(ResearchItem)
            .where(
                ResearchItem.workspace_id == uuid.UUID(workspace_id),
                ResearchItem.content_pillar == pillar_name,
            )
            .order_by(ResearchItem.video_seo_score.desc().nullslast())
            .limit(20)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_rising(self, platform: str = "all", limit: int = 10) -> list:
        """Get rising trends for scheduling. Used by Scheduling engine."""
        workspace_id = await self._get_workspace_id()
        query = (
            select(ResearchItem)
            .where(
                ResearchItem.workspace_id == uuid.UUID(workspace_id),
                ResearchItem.trend_direction == "rising",
            )
        )
        if platform != "all":
            query = query.where(
                (ResearchItem.platform == platform) | (ResearchItem.platform == "all")
            )
        query = (
            query.order_by(ResearchItem.trend_velocity.desc().nullslast())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_top_scoring(self, limit: int = 10, category: str = None) -> list:
        """Get top-scoring research items. Used for content slot generation."""
        workspace_id = await self._get_workspace_id()
        query = select(ResearchItem).where(
            ResearchItem.workspace_id == uuid.UUID(workspace_id),
            ResearchItem.video_seo_score.isnot(None),
        )
        if category:
            query = query.where(ResearchItem.category == category)
        query = (
            query.order_by(ResearchItem.video_seo_score.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_item(self, item_id: str) -> bool:
        """Delete a saved research item by ID."""
        workspace_id = await self._get_workspace_id()

        result = await self.db.execute(
            select(ResearchItem).where(
                ResearchItem.id == uuid.UUID(item_id),
                ResearchItem.workspace_id == uuid.UUID(workspace_id),
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return False

        await self.db.delete(item)
        await self.db.flush()
        return True
