from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.config import settings
from app.services.payhere_service import PayHereService
from app.services.order_service import OrderService
from app.schemas.payment import PaymentVerificationResponse, SimulatorRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/payhere/notify")
async def payhere_webhook_callback(request: Request, db: Session = Depends(get_db)):
    """
    PayHere Server-to-Server Webhook / Notification Callback (notify_url).
    
    PayHere sends payment notifications as 'application/x-www-form-urlencoded'.
    This endpoint verifies the 'md5sig' signature using PayHere's formula and
    updates the order to PAID, FAILED, or CANCELLED based on 'status_code'.
    
    Status codes:
        2  = Success
        0  = Pending
        -1 = Canceled
        -2 = Failed
        -3 = Chargedback
    """
    try:
        # PayHere posts x-www-form-urlencoded data
        form_data = await request.form()
        data_dict = {key: str(value) for key, value in form_data.items()}
    except Exception as e:
        logger.error(f"Error parsing PayHere webhook form data: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data payload")

    if not data_dict:
        # Also check JSON if someone called it directly via JSON
        try:
            data_dict = await request.json()
        except Exception:
            data_dict = {}

    order_id = data_dict.get("order_id")
    status_code = data_dict.get("status_code")
    md5sig = data_dict.get("md5sig")

    if not order_id or not md5sig or not status_code:
        logger.warning(f"PayHere webhook missing critical fields: {data_dict}")
        return Response(content="Missing required callback parameters", status_code=400)

    success, message, order = OrderService.process_payhere_callback(db=db, form_data=data_dict)

    if not success:
        logger.warning(f"PayHere webhook verification failed: {message}")
        return Response(content=f"Callback rejected: {message}", status_code=400)

    logger.info(f"PayHere webhook successfully processed for order {order_id}. New status: {order.status}")
    return Response(content=f"OK: {message}", status_code=200)

@router.post("/simulate", response_model=PaymentVerificationResponse)
def simulate_payhere_payment(sim_in: SimulatorRequest, db: Session = Depends(get_db)):
    """
    PayHere Sandbox Webhook Simulator.
    
    Allows developers and recruiters to simulate a realistic, mathematically valid
    PayHere signed callback on localhost without requiring ngrok tunnel setup.
    Generates authentic 'md5sig' and triggers the real webhook processing logic.
    """
    order = OrderService.get_order_by_number(db, sim_in.order_number)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{sim_in.order_number}' not found"
        )

    # Generate genuine signed callback data
    callback_payload = PayHereService.generate_simulated_callback(
        order=order,
        status_code=sim_in.status_code,
        method=sim_in.method,
        payment_id=sim_in.payment_id,
        card_holder_name=sim_in.card_holder_name or f"{order.first_name} {order.last_name}",
        card_no=sim_in.card_no or "************4242",
        status_message=sim_in.status_message or "Simulated PayHere transaction"
    )

    # Process through standard callback logic
    success, message, updated_order = OrderService.process_payhere_callback(db=db, form_data=callback_payload)

    return PaymentVerificationResponse(
        success=success,
        message=message,
        order_number=order.order_number,
        order_status=updated_order.status if updated_order else order.status,
        payment_id=callback_payload.get("payment_id"),
        signature_valid=success,
        status_code=sim_in.status_code
    )

@router.get("/config/sandbox-info")
def get_sandbox_info():
    """Returns current PayHere sandbox configuration info for frontend displays."""
    return {
        "merchant_id": settings.PAYHERE_MERCHANT_ID,
        "mode": settings.PAYHERE_MODE,
        "currency": settings.PAYHERE_CURRENCY,
        "checkout_url": settings.checkout_url,
        "notify_url": settings.notify_url,
        "base_url": settings.BASE_URL
    }
