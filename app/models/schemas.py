from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class ReelResponse(BaseModel):
    reelId: str
    authorId: str
    hashtags: List[str]
    createdAt: datetime
    layers: List[Dict[str, Any]]
    backgroundAudioUrl: Optional[str] = None

class ReelCreate(BaseModel):
    reelId: str
    authorId: str
    hashtags: List[str]
    layers: List[Dict[str, Any]]
    backgroundAudioUrl: Optional[str] = None

class InteractionCreate(BaseModel):
    user_id: str
    reel_id: str
    interaction_type: str
    view_time_ms: Optional[int] = 0
    hashtags_involved: List[str]

class AIGenerateRequest(BaseModel):
    source: str
