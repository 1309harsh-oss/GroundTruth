import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Any, Union
import jwt
from apps.api.app.core.config import settings

def get_password_hash(password: str) -> str:
    salt = settings.SECRET_KEY[:16]
    derived = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2_sha256${derived.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    if hashed_password.startswith("pbkdf2_sha256$"):
        expected = get_password_hash(plain_password)
        return hmac.compare_digest(expected, hashed_password)
    if hashed_password.startswith("sha256$"):
        calc = "sha256$" + hashlib.sha256(plain_password.encode()).hexdigest()
        return hmac.compare_digest(calc, hashed_password)
    return False

def create_access_token(subject: Union[str, Any], roles: list[str] = [], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "roles": roles}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token
    except jwt.PyJWTError:
        return {}
