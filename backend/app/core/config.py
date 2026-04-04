import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str = secrets.token_hex(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # Featherless.ai
    FEATHERLESS_API_KEY: str = ""
    FEATHERLESS_BASE_URL: str = "https://api.featherless.ai/v1"
    FEATHERLESS_MODEL: str = "deepseek-ai/DeepSeek-V3.2"

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Telegram (free WhatsApp alternative for demo)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_TEST_CHAT_ID: str = ""

    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def async_database_url(self) -> str:
        """
        Convert postgresql:// to postgresql+asyncpg:// and strip query params
        that asyncpg doesn't understand (sslmode, channel_binding).
        SSL is passed via connect_args in database.py instead.
        """
        url = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Strip everything after ? — asyncpg uses connect_args for SSL
        if "?" in url:
            url = url.split("?")[0]
        return url


settings = Settings()
