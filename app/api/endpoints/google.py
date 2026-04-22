from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.models.user import User
from app.services.google import generate_report

router = APIRouter()


@router.get(
    '/',
    response_model=dict,
    summary='Сформировать отчёт в Google Sheets',
    description=(
        'Только для суперпользователей. Создаёт таблицу с закрытыми '
        'проектами, отсортированными по скорости сбора средств.'
    )
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser)
) -> dict:
    """Эндпоинт для формирования отчёта в Google Sheets."""
    spreadsheet_url = await generate_report(session)
    return {'message': 'Отчёт создан', 'url': spreadsheet_url}
