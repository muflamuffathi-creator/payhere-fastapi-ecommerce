from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.payment import Payment
from app.models.product import Product

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Provides key operational and payment gateway metrics for merchant dashboard."""
    total_orders = db.query(Order).count()
    paid_orders = db.query(Order).filter(Order.status == OrderStatus.PAID).count()
    failed_orders = db.query(Order).filter(Order.status == OrderStatus.FAILED).count()
    cancelled_orders = db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count()
    pending_orders = db.query(Order).filter(Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING])).count()

    total_revenue_val = db.query(func.sum(Order.total_amount)).filter(Order.status == OrderStatus.PAID).scalar()
    total_revenue = float(total_revenue_val or 0.0)

    total_products = db.query(Product).count()
    total_payments = db.query(Payment).count()

    conversion_rate = round((paid_orders / total_orders * 100), 1) if total_orders > 0 else 0.0

    recent_payments = (
        db.query(Payment)
        .order_by(Payment.created_at.desc())
        .limit(10)
        .all()
    )

    recent_payments_data = []
    for p in recent_payments:
        order = db.query(Order).filter(Order.id == p.order_id).first()
        recent_payments_data.append({
            "id": p.id,
            "order_number": order.order_number if order else "N/A",
            "payment_id": p.payment_id or "N/A",
            "amount": p.payhere_amount,
            "currency": p.payhere_currency,
            "status_code": p.status_code,
            "method": p.method or "CARD",
            "signature_valid": p.signature_valid,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else "N/A"
        })

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "failed_orders": failed_orders,
        "cancelled_orders": cancelled_orders,
        "pending_orders": pending_orders,
        "conversion_rate": conversion_rate,
        "total_products": total_products,
        "total_payments_logged": total_payments,
        "recent_payments": recent_payments_data
    }
