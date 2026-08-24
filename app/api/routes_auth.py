from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_user_service
from app.api.schemas import TokenResponse, UserCreate, UserRead
from app.application.services import DuplicateEmailError, InvalidCredentialsError, UserService
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, users: UserService = Depends(get_user_service)) -> UserRead:
    try:
        user = users.register(payload.email, payload.password)
    except DuplicateEmailError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    return UserRead(id=user.id, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), users: UserService = Depends(get_user_service)) -> TokenResponse:
    try:
        user = users.authenticate(form.username, form.password)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return TokenResponse(access_token=create_access_token(subject=user.email))
