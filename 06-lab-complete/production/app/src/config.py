from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    openai_model: str
    jwt_secret: str
    jwt_exp_minutes: int
    admin_username: str
    admin_password: str
    user_username: str
    user_password: str


def load_config() -> AppConfig:
    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
        jwt_secret=os.getenv("JWT_SECRET", "change-me-in-production"),
        jwt_exp_minutes=int(os.getenv("JWT_EXP_MINUTES", "60")),
        admin_username=os.getenv("ADMIN_USERNAME", "admin"),
        admin_password=os.getenv("ADMIN_PASSWORD", "admin123"),
        user_username=os.getenv("USER_USERNAME", "user"),
        user_password=os.getenv("USER_PASSWORD", "user123"),
    )
