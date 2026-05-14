import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.domain import Base
from app.core.config import settings

# 1. Grab Railway's variable if it exists, otherwise use your local settings
DATABASE_URL = os.getenv("DATABASE_URL", settings.SQLALCHEMY_DATABASE_URL)

# 2. Fix the URL format (SQLAlchemy crashes if it starts with 'postgres://' instead of 'postgresql://')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Create the engine with the bridged URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()