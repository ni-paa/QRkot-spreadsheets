# app/core/google_client.py
from typing import AsyncGenerator

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

from app.core.config import settings

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

INFO = {
    'type': settings.type,
    'project_id': settings.project_id,
    'private_key_id': settings.private_key_id,
    'private_key': settings.private_key,
    'client_email': settings.client_email,
    'client_id': settings.client_id,
    'auth_uri': settings.auth_uri,
    'token_uri': settings.token_uri,
    'auth_provider_x509_cert_url': settings.auth_provider_x509_cert_url,
    'client_x509_cert_url': settings.client_x509_cert_url,
}


async def get_service() -> AsyncGenerator[Aiogoogle, None]:
    """Асинхронный генератор, возвращающий экземпляр Aiogoogle."""
    creds = ServiceAccountCreds(scopes=SCOPES, **INFO)
    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        yield aiogoogle
