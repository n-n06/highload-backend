from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(route_class=DishkaRoute)


def setup_routers():
    from .locations import router as locations_router
    from .orders import router as orders_router
    from .inventory import router as inventory_router

    router.include_router(locations_router)
    router.include_router(orders_router)
    router.include_router(inventory_router)