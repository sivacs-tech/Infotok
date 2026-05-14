from app.models.domain import Reel
from app.models.schemas import ReelResponse

def map_reel_to_response(reel: Reel) -> ReelResponse:
    return ReelResponse(
        reelId=reel.id,
        authorId=reel.author_id,
        hashtags=reel.hashtags or [],
        createdAt=reel.created_at,
        layers=reel.layers or [],
        backgroundAudioUrl=reel.background_audio_url
    )
