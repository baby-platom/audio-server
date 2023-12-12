from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Common
    DEBUG: bool = False
    API_KEY: str
    LOGGING_LEVEL: str = "INFO"


settings = Settings()
