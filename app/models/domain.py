from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class Reel(Base):
    __tablename__ = "reels"
    id = Column(String, primary_key=True, index=True)
    author_id = Column(String, index=True)
    hashtags = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    layers = Column(JSON) # Stores the JSON objects containing the text/media layer definitions
    background_audio_url = Column(String, nullable=True)

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    reel_id = Column(String, index=True)
    interaction_type = Column(String) # like, view_time, share
    view_time_ms = Column(Integer, default=0)
    hashtags_involved = Column(JSON)
