from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET_STRONG_KEY_FOR_TESTS_ONLY'

    class Config:
        env_file = '.env'


settings = Settings()
