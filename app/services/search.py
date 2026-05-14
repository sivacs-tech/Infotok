from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from app.models.domain import Reel
from typing import List

def search_reels_service(db: Session, query: str) -> List[Reel]:
    q = f"%{query}%"
    reels = db.query(Reel).filter(
        or_(
            cast(Reel.layers, String).ilike(q),
            cast(Reel.hashtags, String).ilike(q)
        )
    ).all()
    return reels
