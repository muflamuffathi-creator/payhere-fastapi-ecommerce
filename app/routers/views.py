from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models.product import Product
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.config import settings

# views.py is at app/routers/views.py → go up 3 levels to reach project root
_this_file = os.path.abspath(__file__)                       # .../app/routers/views.py
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_this_file)))  # .../payhere-fastapi-ecommerce
templates_path = os.path.join(_project_root, "templates")
templates = Jinja2Templates(directory=templates_path)

router = APIRouter(include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    products = ProductService.get_products(db, limit=20)
    categories = [c[0] for c in db.query(Product.category).distinct().all()]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "categories": categories,
            "settings": settings,
        },
    )

@router.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "settings": settings,
        },
    )

@router.get("/checkout/success", response_class=HTMLResponse)
def checkout_success_page(request: Request, order_number: str = "", db: Session = Depends(get_db)):
    order = OrderService.get_order_by_number(db, order_number) if order_number else None
    return templates.TemplateResponse(
        request=request,
        name="order-status.html",
        context={
            "order": order,
            "order_number": order_number,
            "status_type": "success",
            "settings": settings,
        },
    )

@router.get("/checkout/cancel", response_class=HTMLResponse)
def checkout_cancel_page(request: Request, order_number: str = "", db: Session = Depends(get_db)):
    order = OrderService.get_order_by_number(db, order_number) if order_number else None
    return templates.TemplateResponse(
        request=request,
        name="order-status.html",
        context={
            "order": order,
            "order_number": order_number,
            "status_type": "cancelled",
            "settings": settings,
        },
    )

@router.get("/orders/track/{order_number}", response_class=HTMLResponse)
def track_order_page(request: Request, order_number: str, db: Session = Depends(get_db)):
    order = OrderService.get_order_by_number(db, order_number)
    return templates.TemplateResponse(
        request=request,
        name="order-status.html",
        context={
            "order": order,
            "order_number": order_number,
            "status_type": "track",
            "settings": settings,
        },
    )

@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "settings": settings,
        },
    )
