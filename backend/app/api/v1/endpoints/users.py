from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.users import User
from app.schemas.user import UserOut
from app.core.security import get_current_user  # напишем ниже

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return current_user
