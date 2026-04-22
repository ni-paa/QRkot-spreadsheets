from datetime import datetime
from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDCharityProject, process_investment
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
)


DELETE_FORBIDDEN_DETAIL = (
    'В проект были внесены средства, не подлежит удалению!'
)


class CharityProjectServiceError(Exception):
    """Ошибка бизнес-логики целевого проекта (код HTTP и текст для клиента)."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def create_charity_project(
    session: AsyncSession,
    data: CharityProjectCreate,
) -> CharityProject:
    if await CRUDCharityProject.get_by_name(session, data.name):
        raise CharityProjectServiceError(
            HTTPStatus.BAD_REQUEST,
            'Проект с таким именем уже существует!',
        )
    project = await CRUDCharityProject.create(
        session,
        name=data.name,
        description=data.description,
        full_amount=data.full_amount,
    )
    await process_investment(session)
    return await CRUDCharityProject.refresh(session, project)


async def update_charity_project(
    session: AsyncSession,
    project_id: int,
    data: CharityProjectUpdate,
) -> CharityProject:
    project = await CRUDCharityProject.get(session, project_id)
    if not project:
        raise CharityProjectServiceError(
            HTTPStatus.NOT_FOUND,
            'Проект не найден',
        )
    if project.fully_invested:
        raise CharityProjectServiceError(
            HTTPStatus.BAD_REQUEST,
            'Закрытый проект нельзя редактировать!',
        )

    if data.name is not None and data.name != project.name:
        if await CRUDCharityProject.get_by_name_excluding_id(
            session, data.name, project_id
        ):
            raise CharityProjectServiceError(
                HTTPStatus.BAD_REQUEST,
                'Проект с таким именем уже существует!',
            )

    if (
        data.full_amount is not None
        and data.full_amount < project.invested_amount
    ):
        raise CharityProjectServiceError(
            HTTPStatus.BAD_REQUEST,
            'Нелья установить значение full_amount '
            'меньше уже вложенной суммы.',
        )

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.full_amount is not None:
        project.full_amount = data.full_amount
        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()

    return await CRUDCharityProject.update_commit_refresh(session, project)


async def delete_charity_project(
    session: AsyncSession,
    project_id: int,
) -> CharityProject:
    project = await CRUDCharityProject.get(session, project_id)
    if not project:
        raise CharityProjectServiceError(
            HTTPStatus.NOT_FOUND,
            'Проект не найден',
        )
    if project.fully_invested or project.invested_amount > 0:
        raise CharityProjectServiceError(
            HTTPStatus.BAD_REQUEST,
            DELETE_FORBIDDEN_DETAIL,
        )

    await CRUDCharityProject.remove_commit(session, project)
    return project
