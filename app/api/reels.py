from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.utils import map_reel_to_response
from app.core.database import get_db
from app.models.domain import Block, Follow, Reel, User
from app.models.schemas import (
    AIGenerateRequest,
    FeedPageResponse,
    ReelCreate,
    ReelResponse,
)
from app.services.algorithm import get_for_you_feed, get_trending_reels
from app.services.llm import generate_reel_from_source
from app.services.search import search_reels_service

router = APIRouter()


@router.post("/reels", response_model=ReelResponse)
def create_reel(
    reel_in: ReelCreate,
    viewer_id: str | None = None,
    db: Session = Depends(get_db),
):
    author = db.query(User).filter(User.id == reel_in.authorId).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    existing = db.query(Reel).filter(Reel.id == reel_in.reelId).first()
    if existing:
        raise HTTPException(status_code=409, detail="Reel already exists")

    db_reel = Reel(
        id=reel_in.reelId,
        author_id=reel_in.authorId,
        caption=reel_in.caption,
        hashtags=reel_in.hashtags,
        layers=reel_in.layers,
        thumbnail_url=reel_in.thumbnailUrl,
        background_audio_url=reel_in.backgroundAudioUrl,
    )
    db.add(db_reel)
    db.commit()
    db.refresh(db_reel)
    return map_reel_to_response(db_reel, db, viewer_id or reel_in.authorId)


@router.get("/reels/{reel_id}", response_model=ReelResponse)
def get_reel(
    reel_id: str,
    viewer_id: str | None = None,
    db: Session = Depends(get_db),
):
    reel = (
        db.query(Reel)
        .filter(Reel.id == reel_id, Reel.is_deleted == False)  # noqa: E712
        .first()
    )
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    return map_reel_to_response(reel, db, viewer_id)


@router.delete("/reels/{reel_id}")
def delete_reel(reel_id: str, user_id: str, db: Session = Depends(get_db)):
    reel = db.query(Reel).filter(Reel.id == reel_id).first()
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    if reel.author_id != user_id:
        raise HTTPException(status_code=403, detail="Only the author can delete this reel")

    reel.is_deleted = True
    db.commit()
    return {"status": "deleted"}


@router.get("/feed/{user_id}", response_model=FeedPageResponse)
def get_feed(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    feed = get_for_you_feed(db, user_id, page=page, page_size=page_size + 1)
    items = feed[:page_size]
    return FeedPageResponse(
        items=[map_reel_to_response(reel, db, user_id) for reel in items],
        page=page,
        pageSize=page_size,
        hasMore=len(feed) > page_size,
    )


@router.get("/feed/{user_id}/following", response_model=FeedPageResponse)
def get_following_feed(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    following_ids = [
        row.following_id
        for row in db.query(Follow).filter(Follow.follower_id == user_id).all()
    ]
    query = db.query(Reel).filter(Reel.is_deleted == False)  # noqa: E712
    if following_ids:
        query = query.filter(Reel.author_id.in_(following_ids))
    else:
        query = query.filter(False)

    offset = (page - 1) * page_size
    reels = query.order_by(Reel.created_at.desc()).offset(offset).limit(page_size + 1).all()
    items = reels[:page_size]
    return FeedPageResponse(
        items=[map_reel_to_response(reel, db, user_id) for reel in items],
        page=page,
        pageSize=page_size,
        hasMore=len(reels) > page_size,
    )


@router.get("/trending", response_model=FeedPageResponse)
def trending(
    viewer_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    reels = get_trending_reels(db, page=page, page_size=page_size + 1)
    items = reels[:page_size]
    return FeedPageResponse(
        items=[map_reel_to_response(reel, db, viewer_id) for reel in items],
        page=page,
        pageSize=page_size,
        hasMore=len(reels) > page_size,
    )


@router.get("/search", response_model=list[ReelResponse])
def search_reels(
    query: str = Query(...),
    viewer_id: str | None = None,
    db: Session = Depends(get_db),
):
    reels = search_reels_service(db, query)
    return [map_reel_to_response(reel, db, viewer_id) for reel in reels]


@router.get("/hashtags/{tag}/reels", response_model=list[ReelResponse])
def hashtag_reels(
    tag: str,
    viewer_id: str | None = None,
    db: Session = Depends(get_db),
):
    normalized = tag if tag.startswith("#") else f"#{tag}"
    reels = (
        db.query(Reel)
        .filter(Reel.is_deleted == False)  # noqa: E712
        .order_by(Reel.created_at.desc())
        .limit(200)
        .all()
    )
    matches = [reel for reel in reels if normalized in (reel.hashtags or [])]
    return [map_reel_to_response(reel, db, viewer_id) for reel in matches]


@router.get("/users/{user_id}/saved", response_model=list[ReelResponse])
def saved_reels(user_id: str, db: Session = Depends(get_db)):
    from app.models.domain import Bookmark

    reels = (
        db.query(Reel)
        .join(Bookmark, Bookmark.reel_id == Reel.id)
        .filter(Bookmark.user_id == user_id, Reel.is_deleted == False)  # noqa: E712
        .order_by(Bookmark.created_at.desc())
        .all()
    )
    return [map_reel_to_response(reel, db, user_id) for reel in reels]


@router.get("/users/{user_id}/blocked-reels", response_model=list[ReelResponse])
def blocked_filtered_reels(user_id: str, db: Session = Depends(get_db)):
    blocked_ids = [
        row.blocked_id for row in db.query(Block).filter(Block.blocker_id == user_id).all()
    ]
    query = db.query(Reel).filter(Reel.is_deleted == False)  # noqa: E712
    if blocked_ids:
        query = query.filter(~Reel.author_id.in_(blocked_ids))
    reels = query.order_by(Reel.created_at.desc()).limit(100).all()
    return [map_reel_to_response(reel, db, user_id) for reel in reels]


@router.post("/ai/generate-reel", response_model=ReelCreate)
def ai_generate_reel(req: AIGenerateRequest):
    return generate_reel_from_source(req.source)
