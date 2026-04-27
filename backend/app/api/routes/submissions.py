from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.mongo import get_analytics_db
from app.db.session import get_db
from app.models import Project, ProjectSubmission, User
from app.schemas import SubmissionCreate, SubmissionPublic
from app.services.ai_scoring import score_submission
from app.services.realtime import broadcast

router = APIRouter()


@router.get("/me", response_model=list[SubmissionPublic])
async def my_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectSubmission)
        .where(ProjectSubmission.user_id == current_user.id)
        .order_by(desc(ProjectSubmission.created_at))
        .limit(200)
    )
    return list(result.scalars().all())


@router.post("", response_model=SubmissionPublic)
async def submit_project(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_res = await db.execute(select(Project).where(Project.id == payload.project_id))
    project = project_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scored = score_submission(payload.repo_url, payload.documentation_url, payload.tech_stack)
    submission = ProjectSubmission(
        user_id=current_user.id,
        project_id=payload.project_id,
        repo_url=payload.repo_url,
        documentation_url=payload.documentation_url,
        tech_stack=payload.tech_stack,
        ai_score=scored.score,
        ai_feedback=scored.feedback,
        ai_suggestions=scored.suggestions,
        score_breakdown=scored.breakdown,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    # analytics log (Mongo)
    adb = get_analytics_db()
    await adb.activity_logs.insert_one(
        {
            "type": "project_submission",
            "user_id": current_user.id,
            "project_id": payload.project_id,
            "score": scored.score,
        }
    )

    # realtime updates (best-effort)
    await broadcast(
        "leaderboard:update",
        {
            "user_id": current_user.id,
            "project_id": payload.project_id,
            "submission_id": submission.id,
            "score": scored.score,
        },
        room="leaderboard",
    )

    return submission

