from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Verifai API"
    OPENAI_API_KEY: str =""
    TAVILY_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    settings = Settings()

    if (settings.OPENAI_API_KEY == ""):
        raise ValueError("OPENAI_API_KEY must be set")
    if (settings.TAVILY_API_KEY == ""):
        raise ValueError("TAVILY_API_KEY must be set")
    

    return Settings()