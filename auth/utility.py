from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import jwt
import uuid
import logging
from config import Config

# Perbaikan Typo Variable
ACCESS_TOKEN_EXPIRE = 3600

# Setup Password Hashing
password_context = CryptContext(schemes=["argon2"], deprecated="auto")

def generate_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}
    payload['user'] = user_data
    
    # PENTING: Gunakan UTC time aware untuk Serverless/Vercel
    now = datetime.now(timezone.utc)
    
    # Hitung waktu kadaluarsa
    expire_delta = expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRE)
    exp = now + expire_delta

    payload['exp'] = exp
    payload['iat'] = now  # 'Issued At' (Kapan token dibuat)
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh
    
    token = jwt.encode(
        payload,
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            # BUG FIX: 'algorithms' harus berupa LIST, bukan string.
            # Salah: algorithms="HS256" -> Error
            # Benar: algorithms=["HS256"]
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    
    except jwt.ExpiredSignatureError:
        logging.warning("Token expired")
        return None
    except jwt.PyJWTError as e:
        logging.exception(f"JWT Error: {e}")
        return None
    except Exception as e:
        logging.exception(f"Unknown Error decoding token: {e}")
        return None