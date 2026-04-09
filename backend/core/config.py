from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./university.db"
    SECRET_KEY: str = "SUPER_SECRET_KEY_2024" # In production, use environment variables
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    model_config = {"env_file": ".env"}

settings = Settings()
