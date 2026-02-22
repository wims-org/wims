from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import UUID4, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from models import base

ModelType = TypeVar("ModelType", bound=base.SQLModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase[ModelType: base.SQLModelBase, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    db: AsyncSession
    model: type[ModelType]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find(self, id: UUID4) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by(self, kwargs: dict[str, Any]) -> ModelType | None:
        filters = [getattr(self.model, key) == value for key, value in kwargs.items()]
        stmt = select(self.model).where(*filters)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self, where: dict[str, Any] = None, order_by: Any | None = None) -> Sequence[ModelType]:
        if where is None:
            where = {}
        filters = [getattr(self.model, key) == value for key, value in where.items()]
        stmt = select(self.model).where(*filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, data: CreateSchemaType) -> ModelType:
        instance = self.model.model_validate(data)
        self.db.add(instance)
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
        await self.db.refresh(instance)
        return instance

    async def update(
        self,
        instance: ModelType,
        data: UpdateSchemaType,
    ) -> ModelType:
        data_dictionary = data.dict(exclude_unset=True)
        for key, value in data_dictionary.items():
            setattr(instance, key, value)
        self.db.add(instance)
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
        await self.db.refresh(instance)
        return instance

    async def delete(self, id: UUID4) -> ModelType:
        instance = await self.find(id)
        if instance is None:
            raise Exception(f"{self.model.__name__} not found")
        try:
            await self.db.delete(instance)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
        return instance

    async def delete_all(self, where: dict[str, Any]) -> bool:
        filters = [getattr(self.model, key) == value for key, value in where.items()]
        stmt = delete(self.model).where(*filters)
        await self.db.execute(stmt)
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
        return True
