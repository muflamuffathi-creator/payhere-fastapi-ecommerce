import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.config import settings
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.payment import Payment
from app.schemas.order import OrderCreate
from app.services.payhere_service import PayHereService

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def generate_order_number() -> str:
        date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
        random_part = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_part}-{random_part}"

    @classmethod
    def create_order(cls, db: Session, order_in: OrderCreate) -> Order:
        """
        Creates an order with items from product catalog, validating prices from DB.
        """
        if not order_in.items:
            raise HTTPException(status_code=400, detail="An order must contain at least one item.")

        order_number = cls.generate_order_number()
        total_amount = 0.0
        db_items = []

        # Validate stock and calculate authoritative total
        for item_data in order_in.items:
            product = db.query(Product).filter(Product.id == item_data.product_id, Product.is_active == True).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with ID {item_data.product_id} not found or inactive.")
            
            if product.stock_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}, Requested: {item_data.quantity}"
                )

            # Deduct stock
            product.stock_quantity -= item_data.quantity

            subtotal = round(product.price * item_data.quantity, 2)
            total_amount += subtotal

            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=item_data.quantity,
                subtotal=subtotal
            )
            db_items.append(order_item)

        total_amount = round(total_amount, 2)

        order = Order(
            order_number=order_number,
            first_name=order_in.first_name.strip(),
            last_name=order_in.last_name.strip(),
            email=order_in.email.strip().lower(),
            phone=order_in.phone.strip(),
            address=order_in.address.strip(),
            city=order_in.city.strip(),
            country=order_in.country.strip() if order_in.country else "Sri Lanka",
            postal_code=order_in.postal_code.strip() if order_in.postal_code else None,
            total_amount=total_amount,
            currency=settings.PAYHERE_CURRENCY,
            status=OrderStatus.PENDING,
            notes=order_in.notes
        )

        db.add(order)
        db.flush()  # assign order.id

        for item in db_items:
            item.order_id = order.id
            db.add(item)

        db.commit()
        db.refresh(order)
        return order

    @classmethod
    def get_order_by_number(cls, db: Session, order_number: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_number == order_number.strip()).first()

    @classmethod
    def get_order_by_id(cls, db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    @classmethod
    def list_orders(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        query = db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Order.order_number.ilike(search_pattern)) |
                (Order.first_name.ilike(search_pattern)) |
                (Order.last_name.ilike(search_pattern)) |
                (Order.email.ilike(search_pattern)) |
                (Order.phone.ilike(search_pattern))
            )
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return orders, total

    @classmethod
    def process_payhere_callback(cls, db: Session, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Order]]:
        """
        Validates the PayHere webhook callback signature and updates the order status.
        Handles status codes:
            2: Success
            0: Pending
            -1: Canceled
            -2: Failed
            -3: Chargedback
        """
        merchant_id = form_data.get("merchant_id", "")
        order_number = form_data.get("order_id", "")
        payhere_amount = form_data.get("payhere_amount", "")
        payhere_currency = form_data.get("payhere_currency", "")
        status_code_raw = form_data.get("status_code", "")
        received_md5sig = form_data.get("md5sig", "")
        payment_id = form_data.get("payment_id", "")
        method = form_data.get("method", "")
        status_message = form_data.get("status_message", "")
        card_holder_name = form_data.get("card_holder_name", "")
        card_no = form_data.get("card_no", "")

        logger.info(f"Received PayHere Webhook for order: {order_number}, status_code: {status_code_raw}")

        # 1. Verify Signature
        is_signature_valid, calculated_sig = PayHereService.verify_payhere_signature(
            merchant_id=merchant_id,
            order_id=order_number,
            payhere_amount=payhere_amount,
            payhere_currency=payhere_currency,
            status_code=status_code_raw,
            received_md5sig=received_md5sig,
            merchant_secret=settings.PAYHERE_MERCHANT_SECRET
        )

        if not is_signature_valid:
            logger.warning(
                f"PayHere Signature Mismatch for {order_number}! "
                f"Received: {received_md5sig}, Calculated: {calculated_sig}"
            )
            return False, "Signature verification failed", None

        # 2. Locate Order
        order = cls.get_order_by_number(db, order_number)
        if not order:
            logger.error(f"Order not found for PayHere callback: {order_number}")
            return False, f"Order {order_number} not found", None

        # 3. Parse status code
        try:
            status_code = int(status_code_raw)
        except (ValueError, TypeError):
            status_code = -99

        # 4. Record Payment Audit Trail
        payment = Payment(
            order_id=order.id,
            gateway="PayHere",
            payment_id=payment_id,
            payhere_amount=float(payhere_amount) if payhere_amount else order.total_amount,
            payhere_currency=payhere_currency or order.currency,
            status_code=status_code,
            status_message=status_message,
            method=method,
            card_holder_name=card_holder_name,
            card_no=card_no,
            md5sig=received_md5sig,
            signature_valid=is_signature_valid,
            raw_payload=json.dumps(dict(form_data))
        )
        db.add(payment)

        # 5. Transition Order Status
        if status_code == 2:
            # Payment Successful
            order.status = OrderStatus.PAID
            msg = "Payment verified successfully. Order marked as PAID."
        elif status_code == 0:
            order.status = OrderStatus.PROCESSING
            msg = "Payment pending. Order set to PROCESSING."
        elif status_code == -1:
            order.status = OrderStatus.CANCELLED
            cls._restore_stock(db, order)
            msg = "Payment canceled by user. Stock restored."
        elif status_code == -2:
            order.status = OrderStatus.FAILED
            cls._restore_stock(db, order)
            msg = "Payment failed. Stock restored."
        elif status_code == -3:
            order.status = OrderStatus.CANCELLED
            msg = "Payment charged back."
        else:
            msg = f"Unknown status code received: {status_code}"

        db.commit()
        db.refresh(order)
        logger.info(f"Order {order_number} status updated to {order.status}")
        return True, msg, order

    @classmethod
    def _restore_stock(cls, db: Session, order: Order):
        """Restores stock for products in failed or cancelled orders"""
        for item in order.items:
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
