import logging
from asyncio import current_task

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_scoped_session, async_sessionmaker,
                                    create_async_engine)

from app.settings import settings


class DatabaseClient:
    def __init__(self, url: str, echo: bool = False):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        try:
            yield session
        except Exception as e:
            logging.info(e)
            await session.rollback()
        finally:
            await session.close()


database = DatabaseClient(
    url=settings.DB_URL,
    echo=settings.DB.echo,
)
