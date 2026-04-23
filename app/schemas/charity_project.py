from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class BaseCharityProject():
    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(BaseModel, BaseCharityProject):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: PositiveInt


class CharityProjectUpdate(BaseModel, BaseCharityProject):
    name: Optional[str] = Field(None, max_length=100, min_length=1)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[PositiveInt] = None


class CharityProjectDB(BaseModel):
    id: int
    name: str
    description: str
    full_amount: PositiveInt
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
