"""Autenticação JWT simples para o MVP."""
from __future__ import annotations

import jwt
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import bcrypt

from app.config import settings

security = HTTPBearer()

SECRET_KEY = "suportia-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# Credenciais padrão do MVP (mudar em produção!)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"  # Em produção, usar senha forte


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
