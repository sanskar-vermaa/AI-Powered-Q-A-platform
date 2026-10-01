from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_staff
from app.models import Answer, Comment, Flag, Question, User
from app.schemas.flag import FlagCreate, FlagOut, FlagResolve

router = APIRouter(prefix="/api", tags=["moderation"])

TARGETS = {"question": Question, "answer": Answer, "comment": Comment}


@router.post("/flags", response_model=FlagOut, status_code=status.HTTP_201_CREATED)
def create_flag(payload: FlagCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.get(TARGETS[payload.target_type], payload.target_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{payload.target_type.title()} not found")
    duplicate = db.scalar(
        select(Flag).where(
            Flag.reporter_id == user.id,
            Flag.target_type == payload.target_type,
            Flag.target_id == payload.target_id,
            Flag.status == "open",
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already flagged this content")
    flag = Flag(reporter_id=user.id, **payload.model_dump())
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag


@router.get("/moderation/flags", response_model=list[FlagOut], dependencies=[Depends(require_staff)])
def list_flags(
    db: Session = Depends(get_db),
    status_filter: str = Query("open", alias="status", pattern="^(open|resolved|dismissed|all)$"),
):
    stmt = select(Flag)
    if status_filter != "all":
        stmt = stmt.where(Flag.status == status_filter)
    return list(db.scalars(stmt.order_by(Flag.id.desc())))


@router.post("/moderation/flags/{flag_id}", response_model=FlagOut, dependencies=[Depends(require_staff)])
def resolve_flag(flag_id: int, payload: FlagResolve, db: Session = Depends(get_db)):
    flag = db.get(Flag, flag_id)
    if flag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flag not found")
    if payload.delete_content and payload.status == "resolved":
        target = db.get(TARGETS[flag.target_type], flag.target_id)
        if target is not None:
            if isinstance(target, Question):
                target.accepted_answer_id = None
                db.flush()
            elif isinstance(target, Answer) and target.question.accepted_answer_id == target.id:
                target.question.accepted_answer_id = None
                db.flush()
            db.delete(target)
        # Close every other open flag on the content that was just removed.
        for other in db.scalars(
            select(Flag).where(
                Flag.target_type == flag.target_type, Flag.target_id == flag.target_id, Flag.status == "open"
            )
        ):
            other.status = "resolved"
    flag.status = payload.status
    db.commit()
    db.refresh(flag)
    return flag
