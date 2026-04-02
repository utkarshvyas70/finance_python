from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


# ── Base ────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.viewer


# ── Request schemas ─────────────────────────────────────────────────
class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# ── Response schemas ─────────────────────────────────────────────────
class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserOutWithStats(UserOut):
    total_transactions: int = 0