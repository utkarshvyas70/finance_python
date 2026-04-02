from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import (
    CategorySummary,
    FinancialSummary,
    MonthlySummary,
    TransactionOut,
)


def get_financial_summary(
    db: Session,
    user_id: int,
    role: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> FinancialSummary:

    # Base query — admins see all, others see own
    base_query = db.query(Transaction)
    if role != "admin":
        base_query = base_query.filter(Transaction.user_id == user_id)
    if start_date:
        base_query = base_query.filter(Transaction.date >= start_date)
    if end_date:
        base_query = base_query.filter(Transaction.date <= end_date)

    # 1. Total income
    income_query = base_query.filter(Transaction.type == TransactionType.income)
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.id.in_([t.id for t in income_query])
    ).scalar() or 0.0

    # 2. Total expense
    expense_query = base_query.filter(Transaction.type == TransactionType.expense)
    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.id.in_([t.id for t in expense_query])
    ).scalar() or 0.0

    # 3. Category breakdown using DB aggregation
    category_query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
    )
    if role != "admin":
        category_query = category_query.filter(Transaction.user_id == user_id)
    if start_date:
        category_query = category_query.filter(Transaction.date >= start_date)
    if end_date:
        category_query = category_query.filter(Transaction.date <= end_date)

    categories = category_query.group_by(Transaction.category).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    # 4. Monthly totals — SQLite specific strftime
    monthly_query = db.query(
        func.strftime("%Y-%m", Transaction.date).label("month"),
        func.sum(Transaction.amount).filter(
            Transaction.type == TransactionType.income
        ).label("inc"),
        func.sum(Transaction.amount).filter(
            Transaction.type == TransactionType.expense
        ).label("exp"),
    )
    if role != "admin":
        monthly_query = monthly_query.filter(Transaction.user_id == user_id)
    if start_date:
        monthly_query = monthly_query.filter(Transaction.date >= start_date)
    if end_date:
        monthly_query = monthly_query.filter(Transaction.date <= end_date)

    months = monthly_query.group_by("month").order_by("month").all()

    return FinancialSummary(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        current_balance=round(total_income - total_expense, 2),
        total_transactions=base_query.count(),
        category_breakdown=[
            CategorySummary(
                category=c[0],
                total=round(c[1], 2),
                count=c[2],
            )
            for c in categories
        ],
        monthly_totals=[
            MonthlySummary(
                month=m[0],
                income=round(m[1] or 0, 2),
                expense=round(m[2] or 0, 2),
                net=round((m[1] or 0) - (m[2] or 0), 2),
            )
            for m in months
        ],
    )


def get_category_breakdown(
    db: Session,
    user_id: int,
    role: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[CategorySummary]:

    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
    )
    if role != "admin":
        query = query.filter(Transaction.user_id == user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    results = query.group_by(Transaction.category).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    return [
        CategorySummary(
            category=c[0],
            total=round(c[1], 2),
            count=c[2],
        )
        for c in results
    ]


def get_monthly_totals(
    db: Session,
    user_id: int,
    role: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[MonthlySummary]:

    query = db.query(
        func.strftime("%Y-%m", Transaction.date).label("month"),
        func.sum(Transaction.amount).filter(
            Transaction.type == TransactionType.income
        ).label("inc"),
        func.sum(Transaction.amount).filter(
            Transaction.type == TransactionType.expense
        ).label("exp"),
    )
    if role != "admin":
        query = query.filter(Transaction.user_id == user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    results = query.group_by("month").order_by("month").all()

    return [
        MonthlySummary(
            month=m[0],
            income=round(m[1] or 0, 2),
            expense=round(m[2] or 0, 2),
            net=round((m[1] or 0) - (m[2] or 0), 2),
        )
        for m in results
    ]


def get_recent_transactions(
    db: Session,
    user_id: int,
    role: str,
    limit: int = 5,
) -> List[Transaction]:

    query = db.query(Transaction)
    if role != "admin":
        query = query.filter(Transaction.user_id == user_id)

    return query.order_by(Transaction.date.desc()).limit(limit).all()