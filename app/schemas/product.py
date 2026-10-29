from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=150)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock_quantity: int | None = Field(None, ge=0)
    is_active: bool | None = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
