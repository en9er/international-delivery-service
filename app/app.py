from fastapi import APIRouter, FastAPI

from app.routers.parcel_router import parcel_router
from app.settings import settings


def create_app():
    app = FastAPI(
        title='Delivery service',
        version='0.0.1',
        openapi_version='3.0.0',
        docs_url='/docs/swagger',
        openapi_url='/docs/openapi.json'
    )

    main_routers: tuple[APIRouter, ...] = (
        parcel_router,
    )

    for router in main_routers:
        app.include_router(
            router=router,
            prefix=settings.ROOT_PATH
        )
    return app
