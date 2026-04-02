from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenOut
from app.schemas.user import UserCreate, UserOut
from app.services import auth_service
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Register a new user",
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(payload, db)


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Login and get access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(payload, db)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current logged-in user",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user