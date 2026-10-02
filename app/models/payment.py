from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    gateway = Column(String(50), default="PayHere", nullable=False)
    
    # PayHere callback details
    payment_id = Column(String(100), index=True, nullable=True)  # PayHere internal transaction ID
    payhere_amount = Column(Float, nullable=False)
    payhere_currency = Column(String(10), default="LKR", nullable=False)
    status_code = Column(Integer, nullable=False)  # 2: Success, 0: Pending, -1: Canceled, -2: Failed, -3: Chargedback
    status_message = Column(String(255), nullable=True)
    method = Column(String(50), nullable=True)  # VISA, MASTER, EZCASH, etc.
    card_holder_name = Column(String(150), nullable=True)
    card_no = Column(String(50), nullable=True)  # Masked e.g. ************1234
    
    # Verification details
    md5sig = Column(String(100), nullable=True)
    signature_valid = Column(Boolean, default=False, nullable=False)
    raw_payload = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="payments")
