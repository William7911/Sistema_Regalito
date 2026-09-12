from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    role: str

class ProductBase(BaseModel):
    name: str
    barcode: str
    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    current_stock: int
    min_stock: int

class Product(ProductBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class CashRegisterOpen(BaseModel):
    opening_amount: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)
    petty_cash: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)

class CashRegisterClose(BaseModel):
    blind_closing_amount: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)

class CashRegisterResponse(BaseModel):
    id: int
    user_id: int
    opening_time: datetime
    opening_amount: Decimal
    petty_cash: Decimal
    status: str
    closing_time: Optional[datetime] = None
    blind_closing_amount: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)
