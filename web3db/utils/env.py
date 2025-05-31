from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env", env_file_encoding="utf-8", extra="ignore"
    )
    PASSPHRASE: str

    OPENAI_API_KEY: str
    CAPMONSTER_API_KEY: str

    CONNECTION_STRING: str


settings = Settings()
