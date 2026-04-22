# app/services/google.py
from datetime import datetime
from typing import List

from aiogoogle import Aiogoogle
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.google_client import get_service
from app.crud.base import CRUDCharityProject

SPREADSHEET_BODY = {
    'properties': {
        'title': f'Отчёт на {datetime.now().strftime("%d.%m.%Y")}',
    },
    'sheets': [{
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Закрытые проекты',
            'gridProperties': {
                'rowCount': 100,
                'columnCount': 5,
            }
        }
    }]
}

TABLE_HEADERS = [
    'Название проекта',
    'Время сбора (дни)',
    'Описание',
    'Необходимая сумма',
    'Собрано'
]


async def get_projects_data(session: AsyncSession) -> List[dict]:
    """Получает закрытые проекты, сортирует и форматирует данные."""
    projects = await CRUDCharityProject.get_projects_by_completion_rate(
        session
    )
    data = []
    for project in projects:
        # Вычисляем время сбора в днях
        delta = project.close_date - project.create_date
        days = delta.days
        data.append([
            project.name,
            str(days),
            project.description,
            project.full_amount,
            project.invested_amount
        ])
    return data


async def create_spreadsheets(aiogoogle: Aiogoogle) -> str:
    """Создаёт Google таблицу и возвращает её ID."""
    service = await aiogoogle.discover('sheets', 'v4')
    response = await service.spreadsheets.create(json=SPREADSHEET_BODY)
    return response['spreadsheetId']


async def set_user_permissions(
    aiogoogle: Aiogoogle,
    spreadsheet_id: str,
    email: str
) -> None:
    """Выдаёт права на чтение/запись личному аккаунту."""
    service = await aiogoogle.discover('drive', 'v3')
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email
    }
    await service.permissions.create(
        fileId=spreadsheet_id,
        json=permissions_body,
        fields='id'
    )


async def update_spreadsheets_value(
    aiogoogle: Aiogoogle,
    spreadsheet_id: str,
    data: List[List]
) -> None:
    """Заполняет таблицу данными."""
    service = await aiogoogle.discover('sheets', 'v4')
    table_body = {
        'majorDimension': 'ROWS',
        'values': [TABLE_HEADERS] + data
    }
    await service.spreadsheets.values.update(
        spreadsheetId=spreadsheet_id,
        range='A1:E1',
        valueInputOption='USER_ENTERED',
        json=table_body
    )


async def generate_report(session: AsyncSession) -> str:
    """Основная функция формирования отчёта."""
    async with get_service() as aiogoogle:
        # 1. Создаём таблицу
        spreadsheet_id = await create_spreadsheets(aiogoogle)
        # 2. Получаем данные проектов
        projects_data = await get_projects_data(session)
        # 3. Заполняем таблицу
        await update_spreadsheets_value(
            aiogoogle,
            spreadsheet_id,
            projects_data
        )
        # 4. Выдаём права
        from app.core.config import settings
        await set_user_permissions(aiogoogle, spreadsheet_id, settings.email)
        # 5. Возвращаем ссылку на таблицу
        return f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'
