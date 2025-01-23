import os
import secrets
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = f"人大附中数字校园系统"
    DESCRIPTION: str = "人大附中数字校园系统"
    ENV: Literal["development", "staging", "production"] = "development"
    VERSION: str = "0.0.1"
    SECRET_KEY: str = "IHateEverySinglePersonInTheWorld"
    DATABASE_URI: str = "mysql+asyncmy://rdfz3d_main:KpHHrxBwW2PaPZtp@localhost:3306/rdfz3d_main"

    class Config:
        case_sensitive = True


settings = Settings()


class TestSettings(Settings):
    class Config:
        case_sensitive = True


test_settings = TestSettings()
