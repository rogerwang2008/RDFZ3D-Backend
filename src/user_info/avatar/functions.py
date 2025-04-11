from typing import BinaryIO
from PIL import Image

import fastapi_users.models

import universal.config

SAVE_PATH = universal.config.settings.STATIC_DIR / "avatar"
MAX_SIDE_LEN = 512
QUALITY = 85


async def save_avatar(avatar_file_bytes: BinaryIO, file_name: str) -> str:
    avatar_file_bytes.seek(0)
    avatar_file = Image.open(avatar_file_bytes)
    width, height = avatar_file.size
    size = min(width, height)  # 正方形的边长为宽高中较小的值
    left = (width - size) // 2
    top = (height - size) // 2
    right = (width + size) // 2
    bottom = (height + size) // 2
    avatar_file = avatar_file.crop((left, top, right, bottom))

    if avatar_file.width > MAX_SIDE_LEN or avatar_file.height > MAX_SIDE_LEN:
        avatar_file.thumbnail((MAX_SIDE_LEN, MAX_SIDE_LEN), Image.Resampling.LANCZOS)
    avatar_file.save(SAVE_PATH / f"{file_name}.jpg", format="JPEG", progressive=True, quality=QUALITY)
    return f"{file_name}.jpg"
