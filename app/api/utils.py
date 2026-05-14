from sqlalchemy.orm import Session

from app.models.domain import Bookmark, Comment, Follow, Like, Reel, User
from app.models.schemas import ReelResponse, ReelStats, UserResponse, ViewerState


def reel_stats(db: Session, reel_id: str) -> ReelStats:
    return ReelStats(
        likeCount=db.query(Like).filter(Like.reel_id == reel_id).count(),
        commentCount=db.query(Comment).filter(Comment.reel_id == reel_id).count(),
        saveCount=db.query(Bookmark).filter(Bookmark.reel_id == reel_id).count(),
        shareCount=0,
    )


def viewer_state(db: Session, reel: Reel, viewer_id: str | None) -> ViewerState:
    if not viewer_id:
        return ViewerState()

    return ViewerState(
        isLiked=db.query(Like)
        .filter(Like.user_id == viewer_id, Like.reel_id == reel.id)
        .first()
        is not None,
        isFollowing=db.query(Follow)
        .filter(
            Follow.follower_id == viewer_id,
            Follow.following_id == reel.author_id,
        )
        .first()
        is not None,
        isSaved=db.query(Bookmark)
        .filter(Bookmark.user_id == viewer_id, Bookmark.reel_id == reel.id)
        .first()
        is not None,
    )


def map_reel_to_response(
    reel: Reel,
    db: Session,
    viewer_id: str | None = None,
) -> ReelResponse:
    author = db.query(User).filter(User.id == reel.author_id).first()
    return ReelResponse(
        reelId=reel.id,
        authorId=reel.author_id,
        authorUsername=author.username if author else None,
        caption=reel.caption or "",
        hashtags=reel.hashtags or [],
        createdAt=reel.created_at,
        layers=reel.layers or [],
        thumbnailUrl=reel.thumbnail_url,
        backgroundAudioUrl=reel.background_audio_url,
        stats=reel_stats(db, reel.id),
        viewerState=viewer_state(db, reel, viewer_id),
    )


def map_user_to_response(user: User, db: Session) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        displayName=user.display_name,
        avatarUrl=user.avatar_url,
        bio=user.bio or "",
        isGuest=user.is_guest,
        createdAt=user.created_at,
        followerCount=db.query(Follow).filter(Follow.following_id == user.id).count(),
        followingCount=db.query(Follow).filter(Follow.follower_id == user.id).count(),
    )
