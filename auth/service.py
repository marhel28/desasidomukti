from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

# Import internal
from .model import User
from .schema import UserCreate
from .utility import generate_password_hash
# HAPUS IMPORT REDIS

class UserService:
    async def get_all_user(self, session: AsyncSession) -> dict:
        statement = select(User)
        result = await session.exec(statement)
        users = result.all()
        return {"users": users}
    
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user
    
    async def user_exist(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user else False
        
    async def reset_password(self, data, session: AsyncSession):
        email = data.email.strip().lower()
        
        # Query Case Insensitive untuk email
        statement = select(User).where(func.lower(User.email) == email)
        result = await session.exec(statement)
        user = result.first()

        if not user:
            return None
        return {"message": "Fitur reset password butuh update kolom database"}

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        user_dict = user_data.model_dump(exclude_unset=True)

        password_plain = user_dict.pop("password", None)
        if not password_plain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )

        new_user = User(
            **user_dict,
            password=generate_password_hash(password_plain)
        )

        try:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or Email already registered"
            )

        return new_user