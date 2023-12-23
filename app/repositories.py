from sqlalchemy import select, text, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app import logger
from app.models import Parcel, ParcelType, User
from app.pydantic_models.pydantic_models import EParcelType, ParcelPD


class UserRepository:

    @staticmethod
    async def get_or_create(db_session: AsyncSession, session_id) -> User:
        try:
            instance_q = select(User).where(User.session_id == session_id)
            instance = await db_session.scalar(instance_q)
            logger.debug(f'instance: {instance}')
            logger.debug(f'session: {session_id}')
            if instance:
                logger.debug('user found, returning...')
                return instance
            else:
                instance = User(session_id=session_id)
                logger.debug(f'creating user: {instance}')
                db_session.add(instance)
                await db_session.commit()
                return instance
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')
            await db_session.rollback()


class ParcelRepository:

    @staticmethod
    async def create(
            db_session: AsyncSession,
            parcel_instance: ParcelPD,
            parcel_type: int,
            user_session_id: str
    ) -> Parcel:
        parcel = Parcel(
            name=parcel_instance.name,
            weight=parcel_instance.weight,
            parcel_type=parcel_type,
            content_value=parcel_instance.content_cost,
            user_session_id=user_session_id
        )
        logger.debug(f'creating parcel: {parcel}')
        try:
            db_session.add(parcel)
            await db_session.commit()
            await db_session.refresh(parcel)
            return parcel
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')
            await db_session.rollback()

    @staticmethod
    async def get_all_by_session_id(
        db_session: AsyncSession,
        session_id,
        pagination,
        has_delivery_cost: bool = None,
        parcel_type: EParcelType = None
    ):
        try:
            stmt = (
                select(Parcel, ParcelType).join(
                    ParcelType, ParcelType.id == Parcel.parcel_type_id
                ).filter(
                    Parcel.user_session_id == session_id
                )
            )

            if has_delivery_cost:
                stmt = stmt.filter(Parcel.delivery_cost.isnot(None))
            if parcel_type:
                stmt = stmt.filter(ParcelType.name == parcel_type.name)

            stmt = stmt.limit(pagination['limit']).offset(
                pagination['skip_pages']
            )

            result = await db_session.execute(stmt)
            return result.all()
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')

    @staticmethod
    async def get_full_info_by_id(
            db_session: AsyncSession,
            session_id: str,
            parcel_id: int
    ):
        try:
            stmt = (
                select(Parcel, ParcelType).join(
                    ParcelType, ParcelType.id == Parcel.parcel_type_id
                ).filter(
                    Parcel.user_session_id == session_id,
                    Parcel.id == parcel_id
                )
            )
            result = await db_session.execute(stmt)
            return result.one_or_none()
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')

    @staticmethod
    async def calculate_delivery_costs(
            db_session: AsyncSession,
            exchange_rate: float
    ):
        try:
            stmt = update(Parcel).where(
                Parcel.delivery_cost.is_(None)).values(
                delivery_cost=(
                    Parcel.weight * 0.5 + Parcel.content_value * 0.01
                ) * exchange_rate
            )
            await db_session.execute(stmt)
            await db_session.commit()
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')

    @staticmethod
    async def assign_company(
            db_session: AsyncSession,
            company_id: int,
            parcel_id
    ):
        try:
            await db_session.execute(text(
                'SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
            )
            stmt = update(Parcel).where(
                Parcel.id == parcel_id,
                Parcel.delivery_company_id.is_(None)
            ).values(
                delivery_company_id=company_id
            )
            res = await db_session.execute(stmt)
            await db_session.commit()

            if res.rowcount == 0:
                return False
            else:
                return True
        except IntegrityError:
            # todo: too wide
            raise Exception()
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')


class ParcelTypeRepository:
    @staticmethod
    async def get_by_name(db_session: AsyncSession, parcel_type):
        try:
            stmt = select(ParcelType).where(ParcelType.name == parcel_type.name)
            result = await db_session.execute(stmt)
            result = result.scalar_one_or_none()
            return result
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')
            return None

    @staticmethod
    async def get_all(db_session: AsyncSession):
        try:
            stmt = select(ParcelType)
            result = await db_session.execute(stmt)
            result = result.scalars().all()
            return result
        except SQLAlchemyError as e:
            logger.error(f'An error occurred: {e}')
            return None
