from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    redis_url: RedisDsn = "redis://localhost:6379"
    LOGSTASH_HOST: str
    LOGSTASH_PORT: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
