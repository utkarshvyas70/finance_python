from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionCategory, TransactionType


# ── Base ─────────────────────────────────────────────────────────────
class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    category: TransactionCategory
    date: datetime
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(v, 2)


# ── Request schemas ──────────────────────────────────────────────────
class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(v, 2) if v else v


# ── Filter schema (used as query params) ────────────────────────────
class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ── Response schemas ─────────────────────────────────────────────────
class TransactionOut(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Analytics / Summary schemas ──────────────────────────────────────
class CategorySummary(BaseModel):
    category: TransactionCategory
    total: float
    count: int


class MonthlySummary(BaseModel):
    month: str       # e.g. "2024-03"
    income: float
    expense: float
    net: float


class FinancialSummary(BaseModel):
    total_income: float
    total_expense: float
    current_balance: float
    total_transactions: int
    category_breakdown: list[CategorySummary]
    monthly_totals: list[MonthlySummary]