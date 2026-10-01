from sqlalchemy.orm import Session

from app.models import Notification, User


def notify(
    db: Session, user: User | int | None, kind: str, message: str, link: str = "", actor: User | None = None
) -> None:
    """Queue a notification for `user`; skips notifying people about their own actions."""
    if user is None:
        return
    user_id = user if isinstance(user, int) else user.id
    if actor is not None and actor.id == user_id:
        return
    db.add(Notification(user_id=user_id, kind=kind, message=message[:500], link=link))
