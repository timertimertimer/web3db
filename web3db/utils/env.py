from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    PASSPHRASE: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    CAPMONSTER_API_KEY: Optional[str] = None

    CONNECTION_STRING: str


settings = Settings()
