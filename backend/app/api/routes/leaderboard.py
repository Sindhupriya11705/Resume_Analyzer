from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import ProjectSubmission, User

router = APIRouter()


@router.get("/top-projects")
async def top_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSubmission)
        .order_by(desc(ProjectSubmission.ai_score), desc(ProjectSubmission.created_at))
        .limit(50)
    )
    subs = result.scalars().all()
    return [
        {
            "submission_id": s.id,
            "user_id": s.user_id,
            "project_id": s.project_id,
            "score": s.ai_score,
            "created_at": s.created_at,
        }
        for s in subs
    ]


@router.get("/top-students")
async def top_students(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(
            User.id.label("user_id"),
            User.full_name.label("full_name"),
            func.avg(ProjectSubmission.ai_score).label("avg_score"),
            func.count(ProjectSubmission.id).label("submissions"),
        )
        .join(ProjectSubmission, ProjectSubmission.user_id == User.id)
        .group_by(User.id)
        .order_by(desc(func.avg(ProjectSubmission.ai_score)), desc(func.count(ProjectSubmission.id)))
        .limit(50)
    )
    result = await db.execute(stmt)
    rows = result.mappings().all()
    return [
        {
            "user_id": r["user_id"],
            "full_name": r["full_name"],
            "avg_score": float(r["avg_score"] or 0),
            "submissions": int(r["submissions"] or 0),
        }
        for r in rows
    ]

