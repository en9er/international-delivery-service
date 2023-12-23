from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, field_validator


class EParcelType(Enum):
    clothing = 'clothing'
    electronics = 'electronics'
    miscellaneous = 'miscellaneous'


class UserPD(BaseModel):
    session_id: str


class ParcelPD(BaseModel):
    name: str
    weight: float
    parcel_type: EParcelType
    content_cost: float

    @field_validator('weight')
    def weight_validator(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Weight should be positive float')
        return v

    @field_validator('content_cost')
    def content_cost_validator(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Cost should be positive float')
        return v


class ParcelDetailResponse(BaseModel):
    id: Optional[int] = None
    name: str
    weight: float
    parcel_type: str
    content_value: float
    delivery_cost: Union[float, str]
    delivery_company_id: Union[float, str] = None
