from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Project, User
from app.schemas import ProjectCreate, ProjectPublic

router = APIRouter()


@router.get("", response_model=list[ProjectPublic])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(desc(Project.created_at)).limit(200))
    return list(result.scalars().all())


@router.post("", response_model=ProjectPublic)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    project = Project(
        title=payload.title,
        description=payload.description,
        difficulty=payload.difficulty,
        tags=payload.tags,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

