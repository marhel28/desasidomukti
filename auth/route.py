from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime, timezone

from db.main import get_session
from .service import UserService
from .schema import UserCreate, UserLogin, UserRead
from .utility import verify_password, create_access_token
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user


router_user = APIRouter()
user_service = UserService()
REFRESH_TOKEN_DAYS = 2  

@router_user.post('/signup', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    if await user_service.user_exist(email, session):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with this email already exists")

    new_user = await user_service.create_user(user_data, session)
    return new_user


@router_user.post("/login")
async def user_login(
    user_login: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    user = await user_service.get_user_by_email(user_login.email, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email or password wrong"
        )

    # Menggunakan nama fungsi yang sudah diperbaiki
    password_valid = verify_password(
        password=user_login.password,
        hash=user.password
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email or password wrong"
        )

    access_token = create_access_token(
        user_data={
            "email": user.email,
            "uuid": str(user.uuid)
        }
    )

    refresh_token = create_access_token(
        user_data={
            "email": user.email,
            "uuid": str(user.uuid)
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_DAYS)
    )

    return JSONResponse(
        content={
            "message": "Login successful",
            "token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "email": user.email,
                "uuid": str(user.uuid),
                "username": user.username
            }
        }
    )

@router_user.get("/refresh")
async def refresh_access_token(token_detail: dict = Depends(RefreshTokenBearer())):
    expire_timestamp = token_detail["exp"]
    current_time = datetime.now(timezone.utc).timestamp()

    if expire_timestamp > current_time:
        user_data = token_detail["user"]
        
        new_access_token = create_access_token(
            user_data=user_data,
            refresh=False
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            },
            status_code=status.HTTP_200_OK
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Refresh token expired"
    )

@router_user.get('/logout')
async def revoke_token(token_detail: dict = Depends(AccessTokenBearer())):
    return JSONResponse(
        content={
            "message": "Logout successful (Client-side clear)"
        },
        status_code=status.HTTP_200_OK
    )