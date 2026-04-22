# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET_STRONG_KEY_FOR_TESTS_ONLY'

    # Google API credentials
    type: str = ''
    project_id: str = ''
    private_key_id: str = ''
    private_key: str = ''
    client_email: str = ''
    client_id: str = ''
    auth_uri: str = ''
    token_uri: str = ''
    auth_provider_x509_cert_url: str = ''
    client_x509_cert_url: str = ''
    email: str = ''  # для выдачи прав

    class Config:
        env_file = '.env'


settings = Settings()
