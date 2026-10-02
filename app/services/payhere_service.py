import hashlib
import uuid
import logging
from typing import Dict, Any, Tuple
from app.config import settings
from app.models.order import Order

logger = logging.getLogger(__name__)

class PayHereService:
    @staticmethod
    def generate_checkout_hash(
        merchant_id: str,
        order_id: str,
        amount: float,
        currency: str,
        merchant_secret: str
    ) -> str:
        """
        Generates the MD5 hash required for the PayHere Checkout API.
        Formula:
            hashed_secret = UPPER(MD5(merchant_secret))
            formatted_amount = amount formatted with 2 decimal places (e.g., '1000.00')
            hash = UPPER(MD5(merchant_id + order_id + formatted_amount + currency + hashed_secret))
        """
        # Step 1: MD5 hash of merchant_secret in uppercase
        hashed_secret = hashlib.md5(merchant_secret.strip().encode("utf-8")).hexdigest().upper()
        
        # Step 2: Format amount to 2 decimal places without thousands separator
        amount_formatted = f"{float(amount):.2f}"
        
        # Step 3: Concatenate components exactly in order
        raw_string = f"{str(merchant_id).strip()}{str(order_id).strip()}{amount_formatted}{str(currency).strip()}{hashed_secret}"
        
        # Step 4: MD5 hash the string and convert to uppercase
        final_hash = hashlib.md5(raw_string.encode("utf-8")).hexdigest().upper()
        return final_hash

    @staticmethod
    def verify_payhere_signature(
        merchant_id: str,
        order_id: str,
        payhere_amount: str,
        payhere_currency: str,
        status_code: str,
        received_md5sig: str,
        merchant_secret: str
    ) -> Tuple[bool, str]:
        """
        Verifies the PayHere notification callback signature (md5sig).
        Formula:
            hashed_secret = UPPER(MD5(merchant_secret))
            md5sig = UPPER(MD5(merchant_id + order_id + payhere_amount + payhere_currency + status_code + hashed_secret))
        """
        if not received_md5sig:
            return False, "Missing md5sig signature"

        hashed_secret = hashlib.md5(merchant_secret.strip().encode("utf-8")).hexdigest().upper()
        signature_raw = f"{str(merchant_id).strip()}{str(order_id).strip()}{str(payhere_amount).strip()}{str(payhere_currency).strip()}{str(status_code).strip()}{hashed_secret}"
        calculated_md5sig = hashlib.md5(signature_raw.encode("utf-8")).hexdigest().upper()

        is_valid = calculated_md5sig == received_md5sig.strip().upper()
        return is_valid, calculated_md5sig

    @classmethod
    def build_checkout_payload(cls, order: Order, custom_base_url: str = None) -> Dict[str, Any]:
        """
        Constructs all parameters required for PayHere Checkout submission.
        """
        base_url = (custom_base_url or settings.BASE_URL).rstrip("/")
        notify_url = f"{base_url}/api/v1/payments/payhere/notify"
        return_url = f"{base_url}/checkout/success?order_number={order.order_number}"
        cancel_url = f"{base_url}/checkout/cancel?order_number={order.order_number}"

        items_description = ", ".join([f"{item.product_name} (x{item.quantity})" for item in order.items]) or "Store Order"
        if len(items_description) > 250:
            items_description = items_description[:247] + "..."

        amount_str = f"{order.total_amount:.2f}"
        checkout_hash = cls.generate_checkout_hash(
            merchant_id=settings.PAYHERE_MERCHANT_ID,
            order_id=order.order_number,
            amount=order.total_amount,
            currency=order.currency,
            merchant_secret=settings.PAYHERE_MERCHANT_SECRET
        )

        return {
            "checkout_url": settings.checkout_url,
            "merchant_id": settings.PAYHERE_MERCHANT_ID,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url,
            "first_name": order.first_name,
            "last_name": order.last_name,
            "email": order.email,
            "phone": order.phone,
            "address": order.address,
            "city": order.city,
            "country": order.country,
            "order_id": order.order_number,
            "items": items_description,
            "currency": order.currency,
            "amount": amount_str,
            "hash": checkout_hash
        }

    @classmethod
    def generate_simulated_callback(
        cls,
        order: Order,
        status_code: int = 2,
        method: str = "VISA",
        payment_id: str = None,
        card_holder_name: str = "John Doe",
        card_no: str = "************4242",
        status_message: str = "Payment successful"
    ) -> Dict[str, str]:
        """
        Generates a valid, signed PayHere callback payload for testing & simulation.
        """
        merchant_id = settings.PAYHERE_MERCHANT_ID
        order_id = order.order_number
        payhere_amount = f"{order.total_amount:.2f}"
        payhere_currency = order.currency
        status_code_str = str(status_code)
        
        # Calculate valid signature
        hashed_secret = hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.strip().encode("utf-8")).hexdigest().upper()
        sig_raw = f"{merchant_id}{order_id}{payhere_amount}{payhere_currency}{status_code_str}{hashed_secret}"
        md5sig = hashlib.md5(sig_raw.encode("utf-8")).hexdigest().upper()

        return {
            "merchant_id": merchant_id,
            "order_id": order_id,
            "payment_id": payment_id or f"PAYHERE-SIM-{uuid.uuid4().hex[:10].upper()}",
            "payhere_amount": payhere_amount,
            "payhere_currency": payhere_currency,
            "status_code": status_code_str,
            "md5sig": md5sig,
            "custom_1": "Sandbox_Simulator",
            "custom_2": "LankaCart",
            "status_message": status_message,
            "method": method,
            "card_holder_name": card_holder_name,
            "card_no": card_no,
            "card_expiry": "12/28"
        }
