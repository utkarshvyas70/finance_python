"""
User Service
Handles all user management business logic.
Only admins can access these operations (enforced at route level).
"""

from typing import List

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserOutWithStats, UserUpdate
from app.utils.exceptions import BadRequestError, NotFoundError
from app.utils.security import hash_password


def create_user(payload: UserCreate, db: Session) -> UserOut:
    """
    Create a new user (admin operation).
    Raises 400 if email is already registered.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise BadRequestError("A user with this email already exists.")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


def get_all_users(db: Session) -> List[UserOut]:
    """
    Return all users ordered by creation date (newest first).
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserOut.model_validate(u) for u in users]


def get_user_by_id(user_id: int, db: Session) -> UserOutWithStats:
    """
    Return a single user with their total transaction count.
    Raises 404 if user does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User")

    return UserOutWithStats(
        **UserOut.model_validate(user).model_dump(),
        total_transactions=len(user.transactions),
    )


def update_user(user_id: int, payload: UserUpdate, db: Session) -> UserOut:
    """
    Partially update a user's name, role, or active status.
    Only provided fields are updated (PATCH behavior).
    Raises 404 if user does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


def delete_user(user_id: int, db: Session) -> dict:
    """
    Permanently delete a user and all their transactions (cascade).
    Raises 404 if user does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User")

    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully."}