from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

# Import internal
from .utility import decode_token
from .service import UserService
from db.main import get_session
from .model import User 

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, *, bearerFormat=None, scheme_name=None, description=None, auto_error=True):
        super().__init__(bearerFormat=bearerFormat, scheme_name=scheme_name, description=description, auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        cred: HTTPAuthorizationCredentials = await super().__call__(request)
        token = cred.credentials
        
        # Decode token
        token_data = decode_token(token)
        
        # 1. Cek validitas struktur token
        if not self.token_valid(token):  
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        self.verify_token(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        try:
            token_data = decode_token(token)
            # Pastikan payload memiliki key yang dibutuhkan
            return 'user' in token_data and 'email' in token_data['user']
        except Exception:
            return False

    def verify_token(self, token_data: dict):
        raise NotImplementedError("Please override in subclass")


class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict) -> None:
        if token_data.get('refresh'):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Please provide access token, not refresh token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict) -> None:
        if not token_data.get('refresh'):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Please provide refresh token"
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session)
) -> User:
    try:
        user_email = token_details["user"]["email"]
    except (KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Ambil data user terbaru dari Database
    user = await user_service.get_user_by_email(user_email, session)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user