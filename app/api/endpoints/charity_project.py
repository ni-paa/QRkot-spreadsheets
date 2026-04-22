from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.base import CRUDCharityProject
from app.models.user import User
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.charity_project import (
    CharityProjectServiceError,
    create_charity_project as svc_create_charity_project,
    delete_charity_project as svc_delete_charity_project,
    update_charity_project as svc_update_charity_project,
)

router = APIRouter()


def _raise_http(exc: CharityProjectServiceError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail=exc.detail,
    ) from exc


@router.get('/', response_model=List[CharityProjectDB])
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """Показать список всех целевых проектов."""
    return await CRUDCharityProject.get_multi_ordered_by_create_date(session)


@router.post('/', response_model=CharityProjectDB)
async def create_charity_project(
    project_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Создать целевой проект."""
    try:
        return await svc_create_charity_project(session, project_in)
    except CharityProjectServiceError as error:
        _raise_http(error)


@router.patch('/{project_id}', response_model=CharityProjectDB)
async def update_charity_project(
    project_id: int,
    project_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Редактировать целевой проект."""
    try:
        return await svc_update_charity_project(
            session, project_id, project_in
        )
    except CharityProjectServiceError as error:
        _raise_http(error)


@router.delete('/{project_id}', response_model=CharityProjectDB)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Удалить целевой проект."""
    try:
        return await svc_delete_charity_project(session, project_id)
    except CharityProjectServiceError as error:
        _raise_http(error)
