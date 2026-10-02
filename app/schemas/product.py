from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Ceylon Cinnamon Pure Organic Sticks"})
    slug: Optional[str] = Field(None, json_schema_extra={"example": "ceylon-cinnamon-pure-organic-sticks"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Hand-picked grade Alba true Ceylon cinnamon from southern Sri Lanka."})
    category: str = Field(..., json_schema_extra={"example": "Spices"})
    price: float = Field(..., gt=0, json_schema_extra={"example": 2450.00})
    stock_quantity: int = Field(default=50, ge=0, json_schema_extra={"example": 50})
    image_url: Optional[str] = Field(None, json_schema_extra={"example": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=600&q=80"})
    badge: Optional[str] = Field(None, json_schema_extra={"example": "Best Seller"})
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    badge: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
