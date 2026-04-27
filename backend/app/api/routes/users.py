import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import User
from app.schemas import UserPublic, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.github_url is not None:
        current_user.github_url = payload.github_url
    if payload.skill_tags is not None:
        current_user.skill_tags = payload.skill_tags
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/resume", response_model=UserPublic)
async def upload_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
):
    if file.content_type not in {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        raise HTTPException(status_code=400, detail="Upload a PDF or DOCX")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = ".pdf" if file.content_type == "application/pdf" else ".docx"
    name = f"resume_{current_user.id}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, name)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    current_user.resume_path = path
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

