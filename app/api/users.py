from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas import ReelResponse
from app.services.algorithm import get_for_you_feed
from app.api.utils import map_reel_to_response

router = APIRouter()

@router.get("/feed/{user_id}", response_model=List[ReelResponse])
def get_feed(user_id: str, db: Session = Depends(get_db)):
    feed = get_for_you_feed(db, user_id)
    return [map_reel_to_response(r) for r in feed]
