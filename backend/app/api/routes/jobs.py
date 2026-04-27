from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import JobPosting, User
from app.schemas import JobPostingPublic

router = APIRouter()


@router.get("", response_model=list[JobPostingPublic])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobPosting).order_by(desc(JobPosting.created_at)).limit(200))
    return list(result.scalars().all())


@router.get("/me", response_model=list[JobPostingPublic])
async def my_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # simple tag match (production: use ranking + embeddings)
    tags = {t.lower() for t in current_user.skill_tags}
    result = await db.execute(select(JobPosting).order_by(desc(JobPosting.created_at)).limit(500))
    jobs = list(result.scalars().all())
    scored: list[tuple[int, JobPosting]] = []
    for j in jobs:
        jtags = {t.lower() for t in (j.tags or [])}
        score = len(tags.intersection(jtags))
        scored.append((score, j))
    scored.sort(key=lambda x: (x[0], x[1].created_at), reverse=True)
    return [j for s, j in scored[:50] if s > 0] or jobs[:20]

