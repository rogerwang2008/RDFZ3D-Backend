from typing import BinaryIO
from PIL import Image

import fastapi_users.models

import universal.config

SAVE_PATH = universal.config.settings.STATIC_DIR / "avatar"


async def save_avatar(avatar_file_bytes: BinaryIO, file_name: str) -> str:
    avatar_file_bytes.seek(0)
    avatar_file = Image.open(avatar_file_bytes)
    avatar_file.save(SAVE_PATH / f"{file_name}.jpg", format="JPEG", progressive=True)
    return f"{file_name}.jpg"
