"""Configuration comes from environment variables (or a local .env file), never from hard-coded values."""
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET = "dev-only-secret-change-me-0123456789abcdef"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"                   # "development" | "production"
    DATABASE_URL: str = "sqlite:///./student_api.db"
    SECRET_KEY: str = DEV_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 30
    # Optional: create the first admin at startup (free hosting plans give no shell to run a script).
    # Remove ADMIN_PASSWORD from the environment after the first successful deploy.
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    @model_validator(mode="after")
    def check_and_normalise(self):
        # Render / Heroku hand out "postgres://", but SQLAlchemy 2 only understands "postgresql://"
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        # refuse to start in production with the public development secret
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == DEV_SECRET:
            raise ValueError("SECRET_KEY must be set to a private value when ENVIRONMENT=production")
        return self

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
