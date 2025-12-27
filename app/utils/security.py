from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import config
import bcrypt
import hashlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль"""
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_hash.encode(), salt)
    return hashed.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return bcrypt.checkpw(pwd_hash.encode(), hashed_password.encode())

def create_access_token(data: dict) -> str:
    """
    Создаёт JWT токен с payload (sub, username, id, exp).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
