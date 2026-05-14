from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.domain import Reel
from app.models.schemas import ReelCreate, ReelResponse, AIGenerateRequest
from app.api.utils import map_reel_to_response
from app.services.search import search_reels_service
from app.services.llm import generate_reel_from_source

router = APIRouter()

@router.post("/reels", response_model=ReelResponse)
def create_reel(reel_in: ReelCreate, db: Session = Depends(get_db)):
    db_reel = Reel(
        id=reel_in.reelId,
        author_id=reel_in.authorId,
        hashtags=reel_in.hashtags,
        layers=reel_in.layers,
        background_audio_url=reel_in.backgroundAudioUrl
    )
    db.add(db_reel)
    db.commit()
    db.refresh(db_reel)
    return map_reel_to_response(db_reel)

@router.get("/search", response_model=List[ReelResponse])
def search_reels(query: str = Query(...), db: Session = Depends(get_db)):
    reels = search_reels_service(db, query)
    return [map_reel_to_response(r) for r in reels]

@router.post("/ai/generate-reel", response_model=ReelCreate)
def ai_generate_reel(req: AIGenerateRequest):
    reel_data = generate_reel_from_source(req.source)
    return reel_data
