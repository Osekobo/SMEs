from datetime import datetime
from pydantic import BaseModel, Field

class MetaLeadRequest(BaseModel):
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    source: str = Field(default="FACEBOOK", description="FACEBOOK or INSTAGRAM")
    product_interest: str = Field(..., alias="productInterest")

    class Config:
        populate_by_name = True

class LeadResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    source: str
    product_interest: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
