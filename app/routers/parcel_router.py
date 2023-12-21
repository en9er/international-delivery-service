import asyncio

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.database_connector import database

parcel_router = APIRouter(tags=['parcel'], prefix='/parcel')

loop = asyncio.get_event_loop()


@parcel_router.post(
    '/register', status_code=status.HTTP_200_OK, description='Register parcel'
)
async def create_snapshot(
    db_session: AsyncSession = Depends(database.scoped_session_dependency),
):
    return JSONResponse(status_code=200, content=jsonable_encoder('OK'))
