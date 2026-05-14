from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Interaction
from app.models.schemas import InteractionCreate

router = APIRouter()

@router.post("/interactions")
def log_interaction(inter_in: InteractionCreate, db: Session = Depends(get_db)):
    db_inter = Interaction(
        user_id=inter_in.user_id,
        reel_id=inter_in.reel_id,
        interaction_type=inter_in.interaction_type,
        view_time_ms=inter_in.view_time_ms,
        hashtags_involved=inter_in.hashtags_involved
    )
    db.add(db_inter)
    db.commit()
    return {"status": "success"}
