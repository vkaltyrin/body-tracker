from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://localhost:5432/body_training"

    # Пустой токен выключает проверку — так работает локальная разработка.
    # В облаке пустым быть не должен.
    api_token: str = ""

    cors_origins: str = "http://localhost:5173,http://localhost:4317,app://tracker"

    # На Vercel функция живёт коротко и держать соединения нельзя:
    # пул отключается в процессе, пулирует Neon на своей стороне.
    serverless: bool = False

    # Плановые цели недели. Дальше переедут в plan.json.
    target_yoga: int = 7
    target_gym: int = 4

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def settings() -> Settings:
    return Settings()
