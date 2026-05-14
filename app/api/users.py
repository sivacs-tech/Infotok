import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.utils import map_reel_to_response, map_user_to_response
from app.core.database import get_db
from app.models.domain import Follow, Reel, User
from app.models.schemas import ReelResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter()


def _unique_guest_username(db: Session) -> str:
    while True:
        username = f"guest_{uuid.uuid4().hex[:8]}"
        if not db.query(User).filter(User.username == username).first():
            return username


@router.post("/auth/guest", response_model=UserResponse)
def create_guest_user(user_in: UserCreate | None = None, db: Session = Depends(get_db)):
    user_in = user_in or UserCreate()
    username = user_in.username or _unique_guest_username(db)

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = User(
        id=str(uuid.uuid4()),
        username=username,
        display_name=user_in.displayName or username,
        avatar_url=user_in.avatarUrl,
        bio=user_in.bio,
        is_guest=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return map_user_to_response(user, db)


@router.post("/users", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    username = user_in.username or _unique_guest_username(db)

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = User(
        id=str(uuid.uuid4()),
        username=username,
        display_name=user_in.displayName or username,
        avatar_url=user_in.avatarUrl,
        bio=user_in.bio,
        is_guest=user_in.isGuest,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return map_user_to_response(user, db)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return map_user_to_response(user, db)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.username and user_in.username != user.username:
        existing = db.query(User).filter(User.username == user_in.username).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")
        user.username = user_in.username

    if user_in.displayName is not None:
        user.display_name = user_in.displayName
    if user_in.avatarUrl is not None:
        user.avatar_url = user_in.avatarUrl
    if user_in.bio is not None:
        user.bio = user_in.bio
    if user_in.isGuest is not None:
        user.is_guest = user_in.isGuest

    db.commit()
    db.refresh(user)
    return map_user_to_response(user, db)


@router.get("/users/{user_id}/reels", response_model=list[ReelResponse])
def get_user_reels(user_id: str, viewer_id: str | None = None, db: Session = Depends(get_db)):
    reels = (
        db.query(Reel)
        .filter(Reel.author_id == user_id, Reel.is_deleted == False)  # noqa: E712
        .order_by(Reel.created_at.desc())
        .all()
    )
    return [map_reel_to_response(reel, db, viewer_id) for reel in reels]


@router.get("/users/{user_id}/following", response_model=list[UserResponse])
def get_following(user_id: str, db: Session = Depends(get_db)):
    following = (
        db.query(User)
        .join(Follow, Follow.following_id == User.id)
        .filter(Follow.follower_id == user_id)
        .all()
    )
    return [map_user_to_response(user, db) for user in following]
