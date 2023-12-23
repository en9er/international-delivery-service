from asyncio import current_task

from sqlalchemy.ext.asyncio import (AsyncEngine, async_scoped_session,
                                    async_sessionmaker, create_async_engine)
from sqlmodel.ext.asyncio.session import AsyncSession

from app.settings import settings


class DatabaseClient:
    def __init__(self, url: str, echo: bool = False):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
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
        # todo: too wide
        except Exception:
            await session.rollback()
        finally:
            await session.close()


database = DatabaseClient(
    url=settings.DB_URL,
    echo=settings.DB.echo,
)
