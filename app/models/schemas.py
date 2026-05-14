from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    username: str
    displayName: str
    avatarUrl: Optional[str] = None
    bio: str = ""
    isGuest: bool = True
    createdAt: datetime
    followerCount: int = 0
    followingCount: int = 0


class UserCreate(BaseModel):
    username: Optional[str] = None
    displayName: Optional[str] = None
    avatarUrl: Optional[str] = None
    bio: str = ""
    isGuest: bool = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    displayName: Optional[str] = None
    avatarUrl: Optional[str] = None
    bio: Optional[str] = None
    isGuest: Optional[bool] = None


class ReelStats(BaseModel):
    likeCount: int = 0
    commentCount: int = 0
    saveCount: int = 0
    shareCount: int = 0


class ViewerState(BaseModel):
    isLiked: bool = False
    isFollowing: bool = False
    isSaved: bool = False


class ReelResponse(BaseModel):
    reelId: str
    authorId: str
    authorUsername: Optional[str] = None
    caption: str = ""
    hashtags: List[str]
    createdAt: datetime
    layers: List[Dict[str, Any]]
    thumbnailUrl: Optional[str] = None
    backgroundAudioUrl: Optional[str] = None
    stats: ReelStats = Field(default_factory=ReelStats)
    viewerState: ViewerState = Field(default_factory=ViewerState)


class ReelCreate(BaseModel):
    reelId: str
    authorId: str
    caption: str = ""
    hashtags: List[str]
    layers: List[Dict[str, Any]]
    thumbnailUrl: Optional[str] = None
    backgroundAudioUrl: Optional[str] = None


class InteractionCreate(BaseModel):
    user_id: str
    reel_id: str
    interaction_type: str
    view_time_ms: Optional[int] = 0
    hashtags_involved: List[str] = Field(default_factory=list)


class UserAction(BaseModel):
    userId: str


class CommentCreate(BaseModel):
    userId: str
    text: str


class CommentResponse(BaseModel):
    id: int
    userId: str
    username: str
    text: str
    createdAt: datetime


class ReportCreate(BaseModel):
    userId: str
    reason: str = "other"
    details: str = ""


class InteractionState(BaseModel):
    status: str
    active: bool
    stats: ReelStats
    viewerState: ViewerState


class FeedPageResponse(BaseModel):
    items: List[ReelResponse]
    page: int
    pageSize: int
    hasMore: bool


class AIGenerateRequest(BaseModel):
    source: str


class MediaUploadResponse(BaseModel):
    url: str
