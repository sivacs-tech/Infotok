import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def utcnow():
    return datetime.datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, default="")
    is_guest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Reel(Base):
    __tablename__ = "reels"

    id = Column(String, primary_key=True, index=True)
    author_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    caption = Column(Text, default="")
    hashtags = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow, index=True)
    layers = Column(JSON, default=list)
    thumbnail_url = Column(String, nullable=True)
    background_audio_url = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    reel_id = Column(String, ForeignKey("reels.id"), index=True, nullable=False)
    interaction_type = Column(String, index=True, nullable=False)
    view_time_ms = Column(Integer, default=0)
    hashtags_involved = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("user_id", "reel_id", name="uq_like_user_reel"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    reel_id = Column(String, ForeignKey("reels.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    reel_id = Column(String, ForeignKey("reels.id"), index=True, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    following_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "reel_id", name="uq_bookmark_user_reel"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    reel_id = Column(String, ForeignKey("reels.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    reel_id = Column(String, ForeignKey("reels.id"), index=True, nullable=True)
    target_user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    reason = Column(String, default="other")
    details = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_block_pair"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    blocker_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    blocked_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)
