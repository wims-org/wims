from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

import crud
import models


class UsersService:
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, id: str) -> models.database.user.User | None:
        stmt = (
            select(models.database.user.User)
            .where(models.database.user.User.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> models.database.user.User | None:
        stmt = (
            select(models.database.user.User)
            .where(models.database.user.User.email == email)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_users(self) -> list[models.database.user.User]:
        stmt = select(models.database.user.User)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_user(self, payload: models.database.user.UserCreate) -> models.database.user.User | None:
        return await crud.user.UserCRUD(db=self.db).create(payload)

    async def update_user(
        self, instance: models.database.user.User, payload: models.database.user.UserUpdate
    ) -> models.database.user.User:
        return await crud.user.UserCRUD(db=self.db).update(instance, payload)
