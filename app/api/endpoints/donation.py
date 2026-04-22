from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.base import CRUDDonation, process_investment
from app.models.user import User
from app.schemas.donation import (
    DonationCreate,
    DonationDB,
    DonationForUser,
    DonationFullInfoDB,
)


router = APIRouter()


@router.get('/my', response_model=List[DonationForUser])
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Показать пожертвования текущего пользователя."""
    return await CRUDDonation.get_multi_for_user_ordered(session, user.id)


@router.get('/', response_model=List[DonationFullInfoDB])
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Показать список всех пожертвований (только суперпользователь)."""
    return await CRUDDonation.get_multi_ordered_by_create_date(session)


@router.post('/', response_model=DonationDB)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Создать пожертвование."""
    donation = await CRUDDonation.create(
        session,
        full_amount=donation_in.full_amount,
        comment=donation_in.comment,
        user_id=user.id,
    )

    await process_investment(session)

    return await CRUDDonation.refresh(session, donation)
