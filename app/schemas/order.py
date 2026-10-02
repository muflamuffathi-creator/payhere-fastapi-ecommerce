from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class OrderCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=50)
    address: str = Field(..., min_length=5, max_length=300)
    city: str = Field(..., min_length=2, max_length=100)
    country: str = Field(default="Sri Lanka", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_length=1)

class OrderItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

class PaymentSummary(BaseModel):
    id: int
    payment_id: Optional[str] = None
    gateway: str
    payhere_amount: float
    payhere_currency: str
    status_code: int
    status_message: Optional[str] = None
    method: Optional[str] = None
    signature_valid: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    order_number: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    country: str
    postal_code: Optional[str] = None
    total_amount: float
    currency: str
    status: OrderStatus
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    payments: List[PaymentSummary] = []

    model_config = ConfigDict(from_attributes=True)
