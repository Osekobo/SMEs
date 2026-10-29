from datetime import datetime
from pydantic import BaseModel, Field

class OrderCreate(BaseModel):
    phone_number: str
    product_id: int
    quantity: int = Field(..., gt=0)
    delivery_location: str

class OrderResponse(BaseModel):
    id: int
    phone_number: str
    product_id: int
    quantity: int
    total_amount: float
    delivery_location: str
    status: str
    mpesa_receipt: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class MpesaCallbackRequest(BaseModel):
    Body: dict
