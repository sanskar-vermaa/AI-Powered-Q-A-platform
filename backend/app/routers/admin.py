from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import User
from app.schemas.user import UserPrivate

router = APIRouter(prefix="/api/admin", tags=["admin"])


class UserAdminUpdate(BaseModel):
    role: Literal["user", "moderator", "admin"] | None = None
    is_active: bool | None = None


@router.patch("/users/{user_id}", response_model=UserPrivate)
def update_user(user_id: int, payload: UserAdminUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot change your own role or status")
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user
