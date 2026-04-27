from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Course
from app.schemas import CoursePublic

router = APIRouter()


@router.get("", response_model=list[CoursePublic])
async def list_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).order_by(desc(Course.created_at)).limit(200))
    return list(result.scalars().all())

