from typing import Literal
import secrets
import tomllib
import os
import pathlib

from pydantic_settings import BaseSettings

SETTINGS_DIR = pathlib.Path(os.path.dirname(__file__)) / "../../settings.toml"
with open(SETTINGS_DIR, "rb") as f:
    settings_dict = tomllib.load(f)

class Settings(BaseSettings):
    PROJECT_NAME: str = f"人大附中数字校园系统"
    DESCRIPTION: str = "人大附中数字校园系统"
    ENV: Literal["development", "staging", "production"] = "development"
    VERSION: str = "0.0.1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DATABASE_URI: str = (f"mysql+asyncmy://{settings_dict['database']['username']}:{settings_dict['database']['password']}"
                         f"@{settings_dict['database']['host']}:{settings_dict['database']['port']}"
                         f"/{settings_dict['database']['database']}")
    STATIC_DIR: pathlib.Path = SETTINGS_DIR.parent / "static"
    ASSETS_DIR: pathlib.Path = SETTINGS_DIR.parent / "assets"

    ORIGIN_REGEX: str = r"^https?://((localhost|127\.0\.0\.1)(:\d+)?|(.*\.)?x-way\.work)$"

    class Config:
        case_sensitive = True


settings = Settings()


class TestSettings(Settings):
    class Config:
        case_sensitive = True


test_settings = TestSettings()
