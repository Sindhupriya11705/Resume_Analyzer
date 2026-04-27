from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ProjectSubmission, User
from app.services.ai_scoring import recommend_next_skills

router = APIRouter()


class MentorMessage(BaseModel):
    message: str


@router.post("/chat")
async def mentor_chat(
    payload: MentorMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Minimal “mentor”: returns recommendations based on recent performance.
    result = await db.execute(
        select(ProjectSubmission)
        .where(ProjectSubmission.user_id == current_user.id)
        .order_by(desc(ProjectSubmission.created_at))
        .limit(10)
    )
    subs = list(result.scalars().all())
    recent_scores = [s.ai_score for s in subs]
    tech_used = [t for s in subs for t in (s.tech_stack or [])]
    recs = recommend_next_skills(current_user.skill_tags or [], recent_scores, tech_used)

    return {
        "reply": (
            "Here’s a focused next step based on your recent activity: "
            f"learn {', '.join(recs[:3]) if recs else 'one advanced topic'} and build a small project to apply it."
        ),
        "recommended_skills": recs,
        "echo": payload.message[:500],
    }

