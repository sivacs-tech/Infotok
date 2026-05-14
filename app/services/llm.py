import uuid
from app.models.schemas import ReelCreate

def generate_reel_from_source(source: str) -> ReelCreate:
    # MOCKED LLM LOGIC
    # In a production environment, you would invoke the OpenAI/Anthropic API here
    # with a strict system prompt instructing it to return exactly this JSON schema.
    
    headline_layer = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "Breaking News: AI Agents Revolutionize Work",
        "fontFamily": "Roboto",
        "colorHex": "#FFDD00",
        "transform": {"x": 20, "y": 100, "scale": 1.6, "rotation": 0.0, "zIndex": 1},
        "animation": {"entryAnimation": "fade", "durationMillis": 800, "delayMillis": 0}
    }
    
    bullet_1 = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "• Automates routine tasks instantly",
        "fontFamily": "Roboto",
        "colorHex": "#FFFFFF",
        "transform": {"x": 30, "y": 250, "scale": 1.2, "rotation": 0.0, "zIndex": 2},
        "animation": {"entryAnimation": "slide", "durationMillis": 600, "delayMillis": 500}
    }
    
    bullet_2 = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "• Intelligent planning and execution",
        "fontFamily": "Roboto",
        "colorHex": "#FFFFFF",
        "transform": {"x": 30, "y": 350, "scale": 1.2, "rotation": 0.0, "zIndex": 3},
        "animation": {"entryAnimation": "slide", "durationMillis": 600, "delayMillis": 1000}
    }
    
    bullet_3 = {
        "type": "text",
        "id": str(uuid.uuid4()),
        "text": "• Unlocks exponential human productivity",
        "fontFamily": "Roboto",
        "colorHex": "#FFFFFF",
        "transform": {"x": 30, "y": 450, "scale": 1.2, "rotation": 0.0, "zIndex": 4},
        "animation": {"entryAnimation": "slide", "durationMillis": 600, "delayMillis": 1500}
    }
    
    return ReelCreate(
        reelId=str(uuid.uuid4()),
        authorId="ai_agent",
        hashtags=["#ai", "#news", "#tech"],
        layers=[headline_layer, bullet_1, bullet_2, bullet_3],
        backgroundAudioUrl="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    )
