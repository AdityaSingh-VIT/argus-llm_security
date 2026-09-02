"""
auth/dependencies.py — FastAPI dependency for authenticated routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt import decode_token
from database.connection import AsyncSessionLocal
from database import crud
from models.schemas import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    """
    Dependency injected into protected routes.
    Validates the Bearer JWT and returns the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.sub
    except ValueError:
        raise credentials_exception

    async with AsyncSessionLocal() as db:
        user = await crud.get_user_by_username(db, username)

    if user is None:
        raise credentials_exception
    return UserOut.model_validate(user)
