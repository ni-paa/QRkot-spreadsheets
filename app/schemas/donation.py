from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationDB(BaseModel):
    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationForUser(BaseModel):
    """Ответ для списка пожертвований текущего пользователя"""

    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
