from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    APP_NAME: str = "Helix AI API"
    APP_VERSION: str = "0.2.0"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    DATABASE_URL: str | None = None
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "helix"
    POSTGRES_PASSWORD: str = "helix"
    POSTGRES_DB: str = "helix"

    NLP_MODEL_NAME: str = Field(default="ProsusAI/finbert", description="HF model for sentiment inference")
    NLP_PROVIDER: str = Field(
        default="heuristic",
        description="Sentiment provider mode: heuristic, transformers, or auto",
    )
    DEFAULT_BUY_THRESHOLD: float = 0.25
    DEFAULT_SELL_THRESHOLD: float = -0.25
    DEFAULT_MIN_SIGNAL_CONFIDENCE: float = 0.45
    SENTIMENT_HALF_LIFE_HOURS: float = 6.0
    AGGREGATION_CACHE_TTL_SECONDS: int = 30
    API_RATE_LIMIT_PER_MINUTE: int = 120
    AUTO_CREATE_TABLES: bool = False

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
