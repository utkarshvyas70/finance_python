"""
Auth Service
Handles user registration and login business logic.
Passwords are hashed using bcrypt. Tokens are signed JWTs.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import LoginRequest, TokenOut
from app.schemas.user import UserCreate, UserOut
from app.utils.exceptions import BadRequestError, UnauthorizedError
from app.utils.security import create_access_token, hash_password, verify_password


def register_user(payload: UserCreate, db: Session) -> UserOut:
    """
    Register a new user.
    - Checks for duplicate email before creating.
    - Hashes password before storing.
    - Returns the created user (without password).
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


def login_user(payload: LoginRequest, db: Session) -> TokenOut:
    """
    Authenticate a user and return a JWT access token.
    - Verifies email exists and password matches.
    - Checks account is active.
    - Token payload includes email, role, and user_id.
    """
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password.")

    if not user.is_active:
        raise UnauthorizedError("Your account is inactive. Contact an admin.")

    token = create_access_token(data={
        "sub": user.email,
        "role": user.role.value,
        "user_id": user.id,
    })

    return TokenOut(access_token=token)