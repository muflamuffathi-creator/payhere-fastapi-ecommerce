from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class PayHereCheckoutParams(BaseModel):
    checkout_url: str
    merchant_id: str
    return_url: str
    cancel_url: str
    notify_url: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    country: str
    order_id: str
    items: str
    currency: str
    amount: str
    hash: str

class PayHereWebhookPayload(BaseModel):
    merchant_id: str
    order_id: str
    payment_id: str
    payhere_amount: str
    payhere_currency: str
    status_code: str
    md5sig: str
    custom_1: Optional[str] = None
    custom_2: Optional[str] = None
    status_message: Optional[str] = None
    method: Optional[str] = None
    card_holder_name: Optional[str] = None
    card_no: Optional[str] = None
    card_expiry: Optional[str] = None

class PaymentVerificationResponse(BaseModel):
    success: bool
    message: str
    order_number: str
    order_status: str
    payment_id: Optional[str] = None
    signature_valid: bool
    status_code: int

class SimulatorRequest(BaseModel):
    order_number: str
    status_code: int = Field(default=2, description="2: Success, 0: Pending, -1: Canceled, -2: Failed, -3: Chargedback")
    method: str = Field(default="VISA", description="Payment method: VISA, MASTER, AMEX, EZCASH, MCASH")
    payment_id: Optional[str] = Field(default=None, description="Custom payment reference ID")
    card_holder_name: Optional[str] = Field(default="John Doe")
    card_no: Optional[str] = Field(default="************4242")
    status_message: Optional[str] = Field(default="Successfully processed payment")
