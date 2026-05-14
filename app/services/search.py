from typing import List

from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from app.models.domain import Reel, User


def search_reels_service(db: Session, query: str) -> List[Reel]:
    q = f"%{query.strip()}%"
    if q == "%%":
        return []

    return (
        db.query(Reel)
        .join(User, User.id == Reel.author_id)
        .filter(Reel.is_deleted == False)  # noqa: E712
        .filter(
            or_(
                cast(Reel.layers, String).ilike(q),
                cast(Reel.hashtags, String).ilike(q),
                Reel.caption.ilike(q),
                User.username.ilike(q),
                User.display_name.ilike(q),
            )
        )
        .order_by(Reel.created_at.desc())
        .limit(100)
        .all()
    )
