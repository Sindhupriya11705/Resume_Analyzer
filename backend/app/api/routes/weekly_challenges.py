from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import WeeklyChallenge
from app.schemas import WeeklyChallengePublic

router = APIRouter()


@router.get("", response_model=list[WeeklyChallengePublic])
async def list_challenges(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WeeklyChallenge).order_by(desc(WeeklyChallenge.created_at)).limit(200))
    return list(result.scalars().all())

