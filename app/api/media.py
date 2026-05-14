import os
import uuid

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.models.schemas import MediaUploadResponse

router = APIRouter()


@router.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(file: UploadFile = File(...)):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    extension = os.path.splitext(file.filename or "")[1].lower() or ".bin"
    filename = f"{uuid.uuid4().hex}{extension}"
    path = os.path.join(settings.MEDIA_ROOT, filename)

    contents = await file.read()
    with open(path, "wb") as output:
        output.write(contents)

    media_path = f"/media/{filename}"
    url = f"{settings.PUBLIC_BASE_URL}{media_path}" if settings.PUBLIC_BASE_URL else media_path
    return MediaUploadResponse(url=url)
