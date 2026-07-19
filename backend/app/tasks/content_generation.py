"""Celery task to fill empty ContentSlot rows with AI-generated content.
Includes auto-approve logic: slots scoring above threshold are auto-approved
with Post + PostPlatform rows created immediately.
"""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


async def _auto_approve_slot(db, slot, auto_approve_threshold: float):
    """Auto-approve a slot if brand_voice_score meets threshold.
    
    Creates Post + PostPlatform rows and logs the auto-approval.
    Returns True if auto-approved, False otherwise.
    """
    if slot.brand_voice_score and slot.brand_voice_score >= auto_approve_threshold:
        import uuid
        from datetime import datetime
        from app.models.content import Post
        from app.models.post_platform import PostPlatform
        from app.services.audit_log import log_scheduling_action

        slot.status = "approved"
        slot.auto_approved = True
        slot.approved_at = datetime.utcnow()

        # Create parent Post
        post = Post(
            id=str(uuid.uuid4()),
            workspace_id=slot.workspace_id,
            author_id=slot.approved_by or "system",
            content=slot.generated_content or "",
            platform=slot.platform,
            status="scheduled",
            scheduled_at=datetime.combine(
                slot.scheduled_date,
                datetime.min.time().replace(
                    hour=int(slot.scheduled_time.split(":")[0]),
                    minute=int(slot.scheduled_time.split(":")[1]),
                ),
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(post)

        # Create PostPlatform row
        pp = PostPlatform(
            id=str(uuid.uuid4()),
            post_id=post.id,
            workspace_id=slot.workspace_id,
            platform=slot.platform,
            status="scheduled",
            caption=slot.generated_content,
            title=slot.topic,
            scheduled_at=datetime.combine(
                slot.scheduled_date,
                datetime.min.time().replace(
                    hour=int(slot.scheduled_time.split(":")[0]),
                    minute=int(slot.scheduled_time.split(":")[1]),
                ),
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(pp)

        slot.post_id = post.id
        slot.post_platform_id = pp.id

        # Log auto-approval in audit
        try:
            await log_scheduling_action(
                db,
                user_id="system",
                action_type="post_approved",
                description=f"Auto-approved slot {slot.id} ({slot.platform}) — score {slot.brand_voice_score} >= threshold {auto_approve_threshold}",
                metadata={
                    "slot_id": slot.id,
                    "platform": slot.platform,
                    "brand_voice_score": slot.brand_voice_score,
                    "threshold": auto_approve_threshold,
                    "auto_approved": True,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to log auto-approval audit for slot {slot.id}: {e}")

        return True
    else:
        slot.status = "pending_approval"
        return False


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def generate_content_for_plan(self, plan_id: str, workspace_id: str):
    """Generate LLM content for all empty slots in a plan.

    After generation, auto-approves slots where brand_voice_score >=
    strategy.auto_approve_threshold (default 0.85).

    Args:
        plan_id: ContentPlan row ID
        workspace_id: Owning workspace
    """
    import asyncio

    async def _generate():
        from datetime import datetime
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.strategy import ContentPlan, ContentSlot, ContentStrategy
        from app.models.content import BrandVoice
        from app.services.llm_generator import generate_slot_content

        async with AsyncSessionLocal() as db:
            # 1. Fetch plan
            result = await db.execute(
                select(ContentPlan).where(ContentPlan.id == plan_id)
            )
            plan = result.scalar_one_or_none()
            if not plan:
                return {"error": "Plan not found"}

            # 2. Fetch strategy for context + auto-approve threshold
            strat_result = await db.execute(
                select(ContentStrategy).where(ContentStrategy.id == plan.strategy_id)
            )
            strategy = strat_result.scalar_one_or_none()

            # 3. Fetch brand voice
            bv_result = await db.execute(
                select(BrandVoice).where(BrandVoice.workspace_id == workspace_id)
            )
            brand_voice = bv_result.scalar_one_or_none()

            # 4. Fetch empty slots
            slots_result = await db.execute(
                select(ContentSlot).where(
                    ContentSlot.plan_id == plan_id,
                    ContentSlot.status == "empty",
                ).order_by(ContentSlot.scheduled_datetime)
            )
            slots = slots_result.scalars().all()

            if not slots:
                plan.status = "completed"
                plan.generation_progress = {
                    "total_slots": 0,
                    "completed": 0,
                    "current_step": "done",
                }
                await db.commit()
                return {"status": "no_empty_slots"}

            total = len(slots)
            completed = 0
            auto_approved_count = 0
            pending_count = 0

            # Determine auto-approve threshold from strategy
            auto_approve_threshold = getattr(strategy, "auto_approve_threshold", 0.85) if strategy else 0.85

            for slot in slots:
                try:
                    # Build context for LLM (enriched with workspace_id for diversity check)
                    context = {
                        "pillar": slot.pillar_name,
                        "platform": slot.platform,
                        "scheduled_date": str(slot.scheduled_date),
                        "scheduled_time": slot.scheduled_time,
                        "strategy_pillars": strategy.content_pillars if strategy else [],
                        "strategy_goals": strategy.goals if strategy else [],
                        "persona": (strategy.audience_personas or [{}])[0] if strategy else {},
                        "workspace_id": workspace_id,
                        "brand_voice": {
                            "tone": brand_voice.tone if brand_voice else "professional",
                            "style": brand_voice.writing_style if brand_voice else "engaging",
                            "emoji": brand_voice.emoji_usage if brand_voice else "moderate",
                            "sample_posts": (brand_voice.sample_posts or [])[:3] if brand_voice else [],
                        },
                    }

                    generation_result = await generate_slot_content(db, slot, context)

                    if generation_result:
                        slot.generated_content = generation_result["content"]
                        slot.generated_variants = generation_result.get("variants", [])
                        slot.brand_voice_score = generation_result.get("brand_voice_score", 0.0)
                        slot.generation_prompt_used = generation_result.get("prompt_used", "")
                        slot.generation_model = generation_result.get("model", "")
                        slot.generation_tokens = generation_result.get("tokens", 0)
                        slot.topic = generation_result.get("topic", slot.topic)

                        # Auto-approve if score meets threshold
                        was_auto_approved = await _auto_approve_slot(db, slot, auto_approve_threshold)
                        if was_auto_approved:
                            auto_approved_count += 1
                        else:
                            pending_count += 1
                    else:
                        slot.status = "failed"
                        slot.generation_prompt_used = "LLM returned empty response"

                except Exception as e:
                    logger.error(f"Failed to generate for slot {slot.id}: {e}")
                    slot.status = "failed"
                    slot.generation_prompt_used = str(e)

                completed += 1
                # Update progress
                plan.generation_progress = {
                    "total_slots": total,
                    "completed": completed,
                    "current_step": f"generating slot {completed}/{total}",
                }
                await db.flush()

            plan.status = "completed"
            plan.generated_at = datetime.utcnow()
            plan.approved_count = auto_approved_count
            plan.generation_progress = {
                "total_slots": total,
                "completed": completed,
                "current_step": "done",
                "auto_approved": auto_approved_count,
                "pending_approval": pending_count,
            }
            await db.commit()

            logger.info(
                f"Generated content for {completed}/{total} slots in plan {plan_id}: "
                f"{auto_approved_count} auto-approved, {pending_count} pending"
            )
            return {
                "plan_id": plan_id,
                "total": total,
                "completed": completed,
                "auto_approved": auto_approved_count,
                "pending_approval": pending_count,
            }

    try:
        return asyncio.run(_generate())
    except Exception as exc:
        logger.error(f"Content generation failed for plan {plan_id}: {exc}")
        self.retry(exc=exc)
