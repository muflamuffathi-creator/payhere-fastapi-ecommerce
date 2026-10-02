from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.payment import PayHereCheckoutParams
from app.services.order_service import OrderService
from app.services.payhere_service import PayHereService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order with items, reserve stock, and return complete order summary.
    """
    return OrderService.create_order(db=db, order_in=order_in)

@router.get("", response_model=List[OrderResponse])
def list_orders(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, PROCESSING, PAID, FAILED, CANCELLED"),
    search: Optional[str] = Query(None, description="Search by order number or customer name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List recent orders with pagination and filtering."""
    orders, _ = OrderService.list_orders(db=db, skip=skip, limit=limit, status=status, search=search)
    return orders

@router.get("/{order_number}", response_model=OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Fetch complete order details and status by order number."""
    order = OrderService.get_order_by_number(db=db, order_number=order_number)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order '{order_number}' not found")
    return order

@router.get("/{order_number}/checkout-params", response_model=PayHereCheckoutParams)
def get_checkout_params(
    order_number: str,
    request: Request,
    custom_base_url: Optional[str] = Query(None, description="Optional public tunnel URL (e.g., ngrok)"),
    db: Session = Depends(get_db)
):
    """
    Generate authenticated PayHere Checkout payload including the server-computed MD5 hash.
    Used by frontend to submit payment to PayHere Sandbox modal or redirect gateway.
    """
    order = OrderService.get_order_by_number(db=db, order_number=order_number)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order '{order_number}' not found")
    
    # If the user opened via an ngrok URL or supplied one, use it for callbacks
    base_url = custom_base_url or str(request.base_url).rstrip("/")
    payload = PayHereService.build_checkout_payload(order=order, custom_base_url=base_url)
    return payload
