import os

class Settings:
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost/infoscroll_db"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

settings = Settings()
