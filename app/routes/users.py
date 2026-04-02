from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, UserOutWithStats, UserUpdate
from app.services import user_service
from app.utils.dependencies import get_current_user, require_role
from app.utils.responses import success_response

router = APIRouter()


@router.post(
    "/",
    response_model=UserOut,
    status_code=201,
    summary="Create a new user (Admin only)",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.create_user(payload, db)


@router.get(
    "/",
    response_model=List[UserOut],
    summary="List all users (Admin only)",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserOutWithStats,
    summary="Get a user by ID (Admin only)",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.get_user_by_id(user_id, db)


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Update a user (Admin only)",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.update_user(user_id, payload, db)


@router.delete(
    "/{user_id}",
    summary="Delete a user (Admin only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.delete_user(user_id, db)