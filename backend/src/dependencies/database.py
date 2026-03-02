from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dependencies import settings

wims_config = settings.get_settings()

engine = create_async_engine(wims_config.database_uri, future=True, echo=False)


# expire_on_commit=False will prevent attributes from being expired after commit.
AsyncSessionFactory = sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


# Dependency
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


async def get_db(request: Request, db: SessionDep) -> None:
    request.state.db = db
