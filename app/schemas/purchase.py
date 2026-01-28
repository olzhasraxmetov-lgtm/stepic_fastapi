from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.helpers.purchase_status import PurchaseStatus

class PurchaseResponse(BaseModel):
    id: int = Field(..., description="ID покупки")
    course_id: int =  Field(..., description='ID курса')
    user_id: int = Field(..., description='ID пользователя купившего курс')
    purchase_date: datetime = Field(default_factory=datetime.now, description='Дата покупки курса')
    price_paid: Decimal = Field(..., description='Цена на момент покупки курса')

    model_config = ConfigDict(from_attributes=True)

class CourseShortInfo(BaseModel):
    id: int
    title: str
    author_id: int

    model_config = ConfigDict(from_attributes=True)

class PurchaseDetailResponse(BaseModel):
    id: int
    price_paid: Decimal
    status: PurchaseStatus
    purchase_date: datetime
    course: CourseShortInfo
    payment_id: str

    model_config = ConfigDict(from_attributes=True)