import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import interactions, media, reels, users
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.services.seed import seed_database

os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_database(db)

app = FastAPI(title="Infoscroll API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(reels.router, tags=["Reels"])
app.include_router(interactions.router, tags=["Interactions"])
app.include_router(users.router, tags=["Users"])
app.include_router(media.router, tags=["Media"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
