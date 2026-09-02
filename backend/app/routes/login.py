"""
routes/login.py — Authentication endpoints.

POST /auth/login    → username + password → JWT
POST /auth/register → create account + return JWT
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import verify_password, create_access_token, hash_password
from database.connection import get_db
from database import crud
from models.schemas import LoginRequest, TokenResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT access token",
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Argus user",
)
async def register(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed = hash_password(body.password)
    user = await crud.create_user(
        db,
        username=body.username,
        email=f"{body.username}@argus.local",
        hashed_password=hashed,
    )
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)
