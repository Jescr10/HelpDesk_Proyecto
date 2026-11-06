import secrets
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Runtime configuration loaded from environment or a local .env file."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./helpdesk.db"
    jwt_secret: str = Field(default_factory=lambda: secrets.token_hex(32))
    jwt_expire_hours: int = 8

settings = Settings()
