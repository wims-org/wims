from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.database.user import User as UserModel
from models.database.user import UserCreate, UserUpdate

from .base import CRUDBase


class EmailAlreadyExistsError(Exception):
    pass


class UserCRUD(CRUDBase[UserModel, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.model = UserModel

    async def create(self, data: UserCreate) -> UserModel:
        try:
            return await super().create(data)
        except IntegrityError as e:
            if "UniqueViolationError" in str(object=e) and "email" in str(object=e):
                raise EmailAlreadyExistsError(
                    "User with this email already exists. Try signing in with your original SSO provider."
                ) from e
            raise e