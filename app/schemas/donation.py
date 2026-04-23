from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt


class BaseModelDonation():
    comment: Optional[str] = None


class DonationCreate(BaseModel, BaseModelDonation):
    full_amount: PositiveInt

    model_config = ConfigDict(extra='forbid')


class DonationDB(BaseModel, BaseModelDonation):
    id: int
    full_amount: PositiveInt
    create_date: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid',
        exclude_none=True
    )


class DonationForUser(BaseModel, BaseModelDonation):
    """Ответ для списка пожертвований текущего пользователя."""

    id: int
    full_amount: PositiveInt
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
