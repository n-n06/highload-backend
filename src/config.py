from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    ADMIN_PASS: str
    ADMIN_EMAIL: str
    LOGSTASH_HOST: str
    LOGSTASH_PORT: int

    @property
    def db_url_async(self) -> str:
        url = f"""
            postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}
        """
        return url.strip() 

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
