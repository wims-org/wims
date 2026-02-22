from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dependencies import settings

settings = settings.get_settings()
database_uri = f"mariadb+aiomysql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine = create_async_engine(database_uri, future=True, echo=True)


# expire_on_commit=False will prevent attributes from being expired after commit.
AsyncSessionFactory = sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


# Dependency
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session


async def get_db(request: Request, db: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
    request.state.db = db
