from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.utils import reel_stats, viewer_state
from app.core.database import get_db
from app.models.domain import (
    Block,
    Bookmark,
    Comment,
    Follow,
    Interaction,
    Like,
    Reel,
    Report,
    User,
)
from app.models.schemas import (
    CommentCreate,
    CommentResponse,
    InteractionCreate,
    InteractionState,
    ReportCreate,
    UserAction,
)

router = APIRouter()


def _get_reel(db: Session, reel_id: str) -> Reel:
    reel = (
        db.query(Reel)
        .filter(Reel.id == reel_id, Reel.is_deleted == False)  # noqa: E712
        .first()
    )
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    return reel


def _get_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _state(db: Session, reel: Reel, user_id: str, active: bool, status: str):
    return InteractionState(
        status=status,
        active=active,
        stats=reel_stats(db, reel.id),
        viewerState=viewer_state(db, reel, user_id),
    )


@router.post("/interactions")
def log_interaction(inter_in: InteractionCreate, db: Session = Depends(get_db)):
    _get_user(db, inter_in.user_id)
    _get_reel(db, inter_in.reel_id)

    db_inter = Interaction(
        user_id=inter_in.user_id,
        reel_id=inter_in.reel_id,
        interaction_type=inter_in.interaction_type,
        view_time_ms=inter_in.view_time_ms,
        hashtags_involved=inter_in.hashtags_involved,
    )
    db.add(db_inter)
    db.commit()
    return {"status": "success"}


@router.post("/reels/{reel_id}/like", response_model=InteractionState)
def toggle_like(reel_id: str, action: UserAction, db: Session = Depends(get_db)):
    _get_user(db, action.userId)
    reel = _get_reel(db, reel_id)
    existing = (
        db.query(Like)
        .filter(Like.user_id == action.userId, Like.reel_id == reel_id)
        .first()
    )

    if existing:
        db.delete(existing)
        active = False
        status = "unliked"
    else:
        db.add(Like(user_id=action.userId, reel_id=reel_id))
        db.add(
            Interaction(
                user_id=action.userId,
                reel_id=reel_id,
                interaction_type="like",
                hashtags_involved=reel.hashtags or [],
            )
        )
        active = True
        status = "liked"

    db.commit()
    return _state(db, reel, action.userId, active, status)


@router.post("/reels/{reel_id}/save", response_model=InteractionState)
def toggle_save(reel_id: str, action: UserAction, db: Session = Depends(get_db)):
    _get_user(db, action.userId)
    reel = _get_reel(db, reel_id)
    existing = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == action.userId, Bookmark.reel_id == reel_id)
        .first()
    )

    if existing:
        db.delete(existing)
        active = False
        status = "unsaved"
    else:
        db.add(Bookmark(user_id=action.userId, reel_id=reel_id))
        active = True
        status = "saved"

    db.commit()
    return _state(db, reel, action.userId, active, status)


@router.get("/reels/{reel_id}/comments", response_model=list[CommentResponse])
def get_comments(reel_id: str, db: Session = Depends(get_db)):
    _get_reel(db, reel_id)
    comments = (
        db.query(Comment)
        .filter(Comment.reel_id == reel_id)
        .order_by(Comment.created_at.desc())
        .limit(100)
        .all()
    )
    results = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        results.append(
            CommentResponse(
                id=comment.id,
                userId=comment.user_id,
                username=user.username if user else "unknown",
                text=comment.text,
                createdAt=comment.created_at,
            )
        )
    return results


@router.post("/reels/{reel_id}/comments", response_model=CommentResponse)
def add_comment(
    reel_id: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
):
    user = _get_user(db, comment_in.userId)
    reel = _get_reel(db, reel_id)

    text = comment_in.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Comment text is required")

    comment = Comment(user_id=comment_in.userId, reel_id=reel_id, text=text)
    db.add(comment)
    db.add(
        Interaction(
            user_id=comment_in.userId,
            reel_id=reel_id,
            interaction_type="comment",
            hashtags_involved=reel.hashtags or [],
        )
    )
    db.commit()
    db.refresh(comment)
    return CommentResponse(
        id=comment.id,
        userId=user.id,
        username=user.username,
        text=comment.text,
        createdAt=comment.created_at,
    )


@router.post("/users/{target_user_id}/follow")
def toggle_follow(
    target_user_id: str,
    action: UserAction,
    db: Session = Depends(get_db),
):
    _get_user(db, action.userId)
    _get_user(db, target_user_id)

    if action.userId == target_user_id:
        raise HTTPException(status_code=400, detail="Users cannot follow themselves")

    existing = (
        db.query(Follow)
        .filter(
            Follow.follower_id == action.userId,
            Follow.following_id == target_user_id,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        active = False
        status = "unfollowed"
    else:
        db.add(Follow(follower_id=action.userId, following_id=target_user_id))
        active = True
        status = "followed"

    db.commit()
    return {"status": status, "active": active}


@router.post("/reels/{reel_id}/report")
def report_reel(reel_id: str, report_in: ReportCreate, db: Session = Depends(get_db)):
    _get_user(db, report_in.userId)
    reel = _get_reel(db, reel_id)
    db.add(
        Report(
            reporter_id=report_in.userId,
            reel_id=reel.id,
            target_user_id=reel.author_id,
            reason=report_in.reason,
            details=report_in.details,
        )
    )
    db.commit()
    return {"status": "reported"}


@router.post("/users/{target_user_id}/block")
def block_user(
    target_user_id: str,
    action: UserAction,
    db: Session = Depends(get_db),
):
    _get_user(db, action.userId)
    _get_user(db, target_user_id)

    if action.userId == target_user_id:
        raise HTTPException(status_code=400, detail="Users cannot block themselves")

    existing = (
        db.query(Block)
        .filter(Block.blocker_id == action.userId, Block.blocked_id == target_user_id)
        .first()
    )
    if not existing:
        db.add(Block(blocker_id=action.userId, blocked_id=target_user_id))
        db.commit()
    return {"status": "blocked"}
