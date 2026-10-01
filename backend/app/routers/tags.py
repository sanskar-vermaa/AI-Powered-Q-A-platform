from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_staff
from app.models import Tag, question_tags
from app.schemas.tag import TagUpdate, TagWithCount

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagWithCount])
def list_tags(
    db: Session = Depends(get_db),
    q: str | None = Query(None, max_length=35),
    sort: str = Query("popular", pattern="^(popular|name)$"),
    limit: int = Query(50, ge=1, le=200),
):
    count = func.count(question_tags.c.question_id)
    stmt = (
        select(Tag.id, count.label("question_count"))
        .outerjoin(question_tags, question_tags.c.tag_id == Tag.id)
        .group_by(Tag.id, Tag.name)
    )
    if q:
        stmt = stmt.where(Tag.name.ilike(f"%{q.lower()}%"))
    stmt = stmt.order_by(count.desc(), Tag.name) if sort == "popular" else stmt.order_by(Tag.name)
    rows = db.execute(stmt.limit(limit)).all()
    # Text columns (CLOB on Oracle) can't be grouped on, so load the full rows separately.
    tags = {t.id: t for t in db.scalars(select(Tag).where(Tag.id.in_([r.id for r in rows])))}
    return [
        {"id": r.id, "name": tags[r.id].name, "description": tags[r.id].description, "question_count": r.question_count}
        for r in rows
    ]


@router.get("/{name}", response_model=TagWithCount)
def get_tag(name: str, db: Session = Depends(get_db)):
    tag = db.scalar(select(Tag).where(Tag.name == name.lower()))
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    count = db.scalar(select(func.count()).select_from(question_tags).where(question_tags.c.tag_id == tag.id)) or 0
    return {"id": tag.id, "name": tag.name, "description": tag.description, "question_count": count}


@router.patch("/{name}", response_model=TagWithCount, dependencies=[Depends(require_staff)])
def update_tag(name: str, payload: TagUpdate, db: Session = Depends(get_db)):
    tag = db.scalar(select(Tag).where(Tag.name == name.lower()))
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    tag.description = payload.description
    db.commit()
    return get_tag(name, db)
