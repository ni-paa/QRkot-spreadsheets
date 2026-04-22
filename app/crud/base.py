from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


class CRUDBase:
    """Базовый класс CRUD-операций."""

    model_class = None

    @classmethod
    async def get(cls, session: AsyncSession, object_id: int):
        """Получить объект по идентификатору (метод get сессии)."""
        return await session.get(cls.model_class, object_id)

    @classmethod
    async def get_multi(cls, session: AsyncSession):
        """Получить все объекты модели."""
        query_result = await session.execute(select(cls.model_class))
        return query_result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int):
        """Получить объект по идентификатору."""
        query_result = await session.execute(
            select(cls.model_class).where(cls.model_class.id == object_id)
        )
        return query_result.scalars().first()

    @classmethod
    async def refresh(cls, session: AsyncSession, obj):
        await session.refresh(obj)
        return obj


class CRUDCharityProject(CRUDBase):
    """CRUD-операции для проектов."""

    model_class = CharityProject

    @classmethod
    async def get_multi_ordered_by_create_date(
        cls, session: AsyncSession
    ) -> List[CharityProject]:
        result = await session.execute(
            select(CharityProject).order_by(CharityProject.create_date)
        )
        return list(result.scalars().all())

    @classmethod
    async def get_multi_open_ordered_by_create_date(
        cls, session: AsyncSession
    ) -> List[CharityProject]:
        """Открытые проекты, по дате создания."""
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(False))
            .order_by(CharityProject.create_date)
        )
        return list(result.scalars().all())

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str):
        """Получить проект по имени."""
        query_result = await session.execute(
            select(cls.model_class).where(cls.model_class.name == name)
        )
        return query_result.scalars().first()

    @classmethod
    async def get_by_name_excluding_id(
        cls, session: AsyncSession, name: str, exclude_id: int
    ):
        """Проект с заданным именем, исключая запись с указанным id."""
        query_result = await session.execute(
            select(CharityProject).where(
                CharityProject.name == name,
                CharityProject.id != exclude_id,
            )
        )
        return query_result.scalars().first()

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        *,
        name: str,
        description: str,
        full_amount: int,
    ) -> CharityProject:
        project = CharityProject(
            name=name,
            description=description,
            full_amount=full_amount,
        )
        session.add(project)
        await session.flush()
        return project

    @classmethod
    async def update_commit_refresh(
        cls, session: AsyncSession, project: CharityProject
    ) -> CharityProject:
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    @classmethod
    async def remove_commit(
        cls, session: AsyncSession, project: CharityProject
    ) -> CharityProject:
        await session.delete(project)
        await session.commit()


class CRUDDonation(CRUDBase):
    """CRUD-операции для пожертвований."""

    model_class = Donation

    @classmethod
    async def get_multi_for_user_ordered(
        cls, session: AsyncSession, user_id: int
    ) -> List[Donation]:
        result = await session.execute(
            select(Donation)
            .where(Donation.user_id == user_id)
            .order_by(Donation.create_date)
        )
        return list(result.scalars().all())

    @classmethod
    async def get_multi_ordered_by_create_date(
        cls, session: AsyncSession
    ) -> List[Donation]:
        result = await session.execute(
            select(Donation).order_by(Donation.create_date)
        )
        return list(result.scalars().all())

    @classmethod
    async def get_multi_open_ordered_by_create_date(
        cls, session: AsyncSession
    ) -> List[Donation]:
        """Пожертвования с остатком средств, по дате создания."""
        result = await session.execute(
            select(Donation)
            .where(Donation.fully_invested.is_(False))
            .order_by(Donation.create_date)
        )
        return list(result.scalars().all())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        *,
        full_amount: int,
        comment: Optional[str],
        user_id: int,
    ) -> Donation:
        donation = Donation(
            full_amount=full_amount,
            comment=comment,
            user_id=user_id,
        )
        session.add(donation)
        await session.flush()
        return donation


async def process_investment(session: AsyncSession) -> None:
    """Распределить свободные средства пожертвований по открытым проектам."""
    projects = await CRUDCharityProject.get_multi_open_ordered_by_create_date(
        session
    )
    donations = await CRUDDonation.get_multi_open_ordered_by_create_date(
        session
    )

    for project in projects:
        for donation in donations:
            if donation.fully_invested:
                continue
            if project.fully_invested:
                break

            donation_remaining = (
                donation.full_amount - donation.invested_amount
            )
            project_remaining = (
                project.full_amount - project.invested_amount
            )

            invest_amount = min(donation_remaining, project_remaining)

            project.invested_amount += invest_amount
            if project.invested_amount >= project.full_amount:
                project.fully_invested = True
                project.close_date = datetime.now()

            donation.invested_amount += invest_amount
            if donation.invested_amount >= donation.full_amount:
                donation.fully_invested = True
                donation.close_date = datetime.now()

    await session.commit()
