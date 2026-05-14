import uuid

from sqlalchemy.orm import Session

from app.models.domain import Reel, User


def seed_database(db: Session):
    if db.query(User).first() or db.query(Reel).first():
        return

    creators = [
        User(
            id=str(uuid.uuid4()),
            username="creator_1",
            display_name="Creator One",
            is_guest=False,
            bio="Flutter, dev, and short-form explainers.",
        ),
        User(
            id=str(uuid.uuid4()),
            username="design_guru",
            display_name="Design Guru",
            is_guest=False,
            bio="Motion and interface ideas.",
        ),
        User(
            id=str(uuid.uuid4()),
            username="tech_future",
            display_name="Tech Future",
            is_guest=False,
            bio="Fresh takes on agentic software.",
        ),
    ]
    db.add_all(creators)
    db.flush()

    reels = [
        Reel(
            id=str(uuid.uuid4()),
            author_id=creators[0].id,
            caption="Welcome to Infoscroll!",
            hashtags=["#flutter", "#dev", "#ai"],
            background_audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            layers=[
                {
                    "type": "text",
                    "id": str(uuid.uuid4()),
                    "text": "Welcome to Infoscroll!",
                    "fontFamily": "Roboto",
                    "colorHex": "#FFFFFF",
                    "transform": {"x": 50, "y": 300, "scale": 1.5, "rotation": 0.0, "zIndex": 1},
                    "animation": {"entryAnimation": "fade", "durationMillis": 1000, "delayMillis": 200},
                }
            ],
        ),
        Reel(
            id=str(uuid.uuid4()),
            author_id=creators[1].id,
            caption="Swipe down for more",
            hashtags=["#design", "#uiux", "#motion"],
            background_audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            layers=[
                {
                    "type": "text",
                    "id": str(uuid.uuid4()),
                    "text": "Swipe down for more",
                    "fontFamily": "Roboto",
                    "colorHex": "#FFDD00",
                    "transform": {"x": 60, "y": 400, "scale": 1.2, "rotation": 0.0, "zIndex": 1},
                    "animation": {"entryAnimation": "slide", "durationMillis": 800, "delayMillis": 0},
                }
            ],
        ),
        Reel(
            id=str(uuid.uuid4()),
            author_id=creators[2].id,
            caption="The Future is Agentic",
            hashtags=["#tech", "#future", "#agentic"],
            background_audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            layers=[
                {
                    "type": "text",
                    "id": str(uuid.uuid4()),
                    "text": "The Future is Agentic",
                    "fontFamily": "Roboto",
                    "colorHex": "#00FFDD",
                    "transform": {"x": 40, "y": 250, "scale": 1.8, "rotation": 0.1, "zIndex": 1},
                    "animation": {"entryAnimation": "scale", "durationMillis": 1200, "delayMillis": 300},
                }
            ],
        ),
    ]
    db.add_all(reels)
    db.commit()
