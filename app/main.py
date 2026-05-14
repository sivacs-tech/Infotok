import os

import uvicorn
from fastapi import FastAPI
from app.core.database import Base, engine
from app.api import reels, users, interactions

# Initialize DB schemas automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Infoscroll API", version="1.0.0")

# Mount API routers securely
app.include_router(reels.router, tags=["Reels"])
app.include_router(interactions.router, tags=["Interactions"])
app.include_router(users.router, tags=["Users"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
