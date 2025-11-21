from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from .locations import router as locations_router
from .orders import router as orders_router
from .inventory import router as inventory_router

router = APIRouter(route_class=DishkaRoute)

router.include_router(locations_router)
router.include_router(orders_router)
router.include_router(inventory_router)
