from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.exceptions import ForbiddenError, UnauthorizedError
from app.utils.security import decode_access_token

# Use HTTPBearer so Swagger shows the correct Authorize box
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedError("Invalid or expired token.")

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")

    return user


def require_role(*roles: UserRole):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"Access denied. Required role(s): {[r.value for r in roles]}"
            )
        return current_user
    return role_checker