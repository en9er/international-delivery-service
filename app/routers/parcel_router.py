import asyncio

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app import logger
from app.db import database
from app.pydantic_models.pydantic_models import (EParcelType,
                                                 ParcelDetailResponse,
                                                 ParcelPD)
from app.repositories import (ParcelRepository, ParcelTypeRepository,
                              UserRepository)

parcel_router = APIRouter(tags=['parcel'], prefix='/parcel')

loop = asyncio.get_event_loop()


def pagination_params(limit: int = 10, skip_pages: int = 0):
    return {'limit': limit, 'skip_pages': skip_pages}


@parcel_router.post(
    '/register', status_code=status.HTTP_200_OK, description='Register parcel'
)
async def register_parcel(
    request: Request,
    parcel_filter: ParcelPD,
    db_session: AsyncSession = Depends(database.scoped_session_dependency),
    user_repo: UserRepository = Depends(),
    parcel_type_repo: ParcelTypeRepository = Depends(),
    parcel_repo: ParcelRepository = Depends(),
):
    logger.info(request.state)
    session_id = request.cookies.get('session_id')
    try:
        user = await user_repo.get_or_create(db_session, session_id)

        parcel_type = await parcel_type_repo.get_by_name(
            db_session, parcel_filter.parcel_type
        )
        if parcel_type:
            created_parcel = await parcel_repo.create(
                db_session, parcel_filter, parcel_type, user.session_id
            )
        else:
            return JSONResponse(
                status_code=404,
                content=jsonable_encoder(
                    f'Parcel type {parcel_type} not found'
                ),
            )
    except SQLAlchemyError as e:
        return JSONResponse(status_code=500, content=jsonable_encoder(e))

    return JSONResponse(
        status_code=200, content=jsonable_encoder(created_parcel.id)
    )


@parcel_router.get(
    '/parcel-types',
    status_code=status.HTTP_200_OK,
    description='Get parcel types'
)
async def get_parcel_types(
    db_session: AsyncSession = Depends(database.scoped_session_dependency),
    parcel_repo: ParcelTypeRepository = Depends(),
):
    parcels = await parcel_repo.get_all(db_session)
    return JSONResponse(status_code=200, content=jsonable_encoder(parcels))


@parcel_router.get(
    '/user-parcels',
    status_code=status.HTTP_200_OK,
    description='Get user parcels'
)
async def get_user_parcels(
    request: Request,
    pagination: dict = Depends(pagination_params),
    db_session: AsyncSession = Depends(database.scoped_session_dependency),
    parcel_repo: ParcelRepository = Depends(),
    parcel_type: EParcelType = Query(None, alias='parcel_type'),
    has_delivery_cost: bool = Query(None, alias='has_delivery_cost'),
):
    session_id = request.cookies.get('session_id')
    parcels_res = await parcel_repo.get_all_by_session_id(
        db_session, session_id, pagination, has_delivery_cost, parcel_type
    )

    serialized_parcels = [
        ParcelDetailResponse(
            id=parcel.id,
            name=parcel.name,
            weight=parcel.weight,
            parcel_type=parcel_type.name,
            content_value=parcel.content_value,
            delivery_cost=parcel.delivery_cost
            if parcel.delivery_cost
            else 'No info yet.',
            delivery_company_id=parcel.delivery_company_id
            if parcel.delivery_company_id
            else 'Not assigned yet.',
        )
        for parcel, parcel_type in parcels_res
    ]
    return JSONResponse(
        status_code=200, content=jsonable_encoder(serialized_parcels)
    )


@parcel_router.get(
    '/parcel-by-id',
    status_code=status.HTTP_200_OK,
    description='Get user parcel by id'
)
async def get_user_parcel_by_id(
    request: Request,
    parcel_id: int,
    db_session: AsyncSession = Depends(database.scoped_session_dependency),
    parcel_repo: ParcelRepository = Depends(),
):
    session_id = request.cookies.get('session_id')
    parcel_res = await parcel_repo.get_full_info_by_id(
        db_session, session_id, parcel_id
    )
    if parcel_res:
        parcel, parcel_type = parcel_res
        return ParcelDetailResponse(
            id=None,
            name=parcel.name,
            weight=parcel.weight,
            parcel_type=parcel_type.name,
            content_value=parcel.content_value,
            delivery_cost=parcel.delivery_cost
            if parcel.delivery_cost
            else 'No info yet.',
            delivery_company_id=parcel.delivery_company_id
            if parcel.delivery_company_id
            else 'Not assigned yet.',
        ).model_dump(exclude_none=True)
    else:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(f'Parcel with id {parcel_id} not found'),
        )


@parcel_router.put(
    '/assign-company',
    status_code=status.HTTP_200_OK,
    description='Assign delivery company to parcel',
)
async def assign_delivery_company(
    parcel_id: int,
    company_id,
    db_session: AsyncSession = Depends(database.scoped_session_dependency),
    parcel_repo: ParcelRepository = Depends(),
):

    try:
        update_res = await parcel_repo.assign_company(
            db_session, company_id, parcel_id
        )
        if update_res:
            return JSONResponse(status_code=200, content=jsonable_encoder('OK'))
        else:
            return JSONResponse(
                status_code=409, content=jsonable_encoder('Conflict')
            )

    # todo: too wide
    except Exception:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(f'Company with id {company_id} not found'),
        )
