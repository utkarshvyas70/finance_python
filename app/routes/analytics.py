from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.transaction import (
    CategorySummary,
    FinancialSummary,
    MonthlySummary,
    TransactionOut,
)
from app.services import analytics_service
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/summary",
    response_model=FinancialSummary,
    summary="Get full financial summary — balance, income, expenses, breakdown",
)
def get_summary(
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_financial_summary(
        db=db,
        user_id=current_user.id,
        role=current_user.role.value,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/category-breakdown",
    response_model=List[CategorySummary],
    summary="Get total spending and count grouped by category",
)
def get_category_breakdown(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_category_breakdown(
        db=db,
        user_id=current_user.id,
        role=current_user.role.value,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/monthly",
    response_model=List[MonthlySummary],
    summary="Get month-by-month income vs expense totals",
)
def get_monthly_totals(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_monthly_totals(
        db=db,
        user_id=current_user.id,
        role=current_user.role.value,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/recent",
    response_model=List[TransactionOut],
    summary="Get most recent N transactions",
)
def get_recent(
    limit: int = Query(5, ge=1, le=50, description="Number of recent transactions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = analytics_service.get_recent_transactions(
        db=db,
        user_id=current_user.id,
        role=current_user.role.value,
        limit=limit,
    )
    return [TransactionOut.model_validate(t) for t in transactions]