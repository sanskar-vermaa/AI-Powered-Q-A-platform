from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tag
from app.utils.text import normalize_tags


def get_or_create_tags(db: Session, raw_tags: list[str]) -> list[Tag]:
    names = normalize_tags(raw_tags)
    if not names:
        return []
    existing = {t.name: t for t in db.scalars(select(Tag).where(Tag.name.in_(names)))}
    tags = []
    for name in names:
        tag = existing.get(name)
        if tag is None:
            tag = Tag(name=name, description="")
            db.add(tag)
        tags.append(tag)
    return tags
