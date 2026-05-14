import uuid

from app.models.schemas import ReelCreate


def generate_reel_from_source(source: str) -> ReelCreate:
    headline = source.strip()[:80] or "AI Agents Revolutionize Work"

    headline_layer = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": headline,
        "fontFamily": "Roboto",
        "colorHex": "#FFDD00",
        "transform": {"x": 20, "y": 100, "scale": 1.4, "rotation": 0.0, "zIndex": 1},
        "animation": {"entryAnimation": "fade", "durationMillis": 800, "delayMillis": 0},
    }

    bullet_1 = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "- Turns source material into a short reel",
        "fontFamily": "Roboto",
        "colorHex": "#FFFFFF",
        "transform": {"x": 30, "y": 250, "scale": 1.1, "rotation": 0.0, "zIndex": 2},
        "animation": {"entryAnimation": "slide", "durationMillis": 600, "delayMillis": 500},
    }

    bullet_2 = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "- Highlights the main idea clearly",
        "fontFamily": "Roboto",
        "colorHex": "#FFFFFF",
        "transform": {"x": 30, "y": 350, "scale": 1.1, "rotation": 0.0, "zIndex": 3},
        "animation": {"entryAnimation": "slide", "durationMillis": 600, "delayMillis": 1000},
    }

    bullet_3 = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "- Ready to edit before publishing",
        "fontFamily": "Roboto",
        "colorHex": "#FFFFFF",
        "transform": {"x": 30, "y": 450, "scale": 1.1, "rotation": 0.0, "zIndex": 4},
        "animation": {"entryAnimation": "slide", "durationMillis": 600, "delayMillis": 1500},
    }

    return ReelCreate(
        reelId=str(uuid.uuid4()),
        authorId="ai_agent",
        caption=headline,
        hashtags=["#ai", "#news", "#tech"],
        layers=[headline_layer, bullet_1, bullet_2, bullet_3],
        backgroundAudioUrl="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    )
