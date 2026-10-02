from app.routers.products import router as products_router
from app.routers.orders import router as orders_router
from app.routers.payments import router as payments_router
from app.routers.admin import router as admin_router
from app.routers.views import router as views_router

__all__ = ["products_router", "orders_router", "payments_router", "admin_router", "views_router"]
