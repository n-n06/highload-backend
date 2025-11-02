from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    LOGSTASH_HOST: str
    LOGSTASH_PORT: int
    SECRET: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
