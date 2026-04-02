"""
Transaction Service
Handles all transaction CRUD operations with filtering and pagination.
Role-based data scoping is enforced here:
  - Admins see all transactions
  - All other roles see only their own
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionCategory, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionOut, TransactionUpdate
from app.utils.exceptions import NotFoundError


def create_transaction(
    payload: TransactionCreate,
    user_id: int,
    db: Session,
) -> TransactionOut:
    """
    Create a new financial transaction for the given user.
    Amount is validated (> 0) at the schema level.
    """
    transaction = Transaction(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
        user_id=user_id,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return TransactionOut.model_validate(transaction)


def get_all_transactions(
    db: Session,
    user_id: int,
    role: str,
    type: Optional[TransactionType] = None,
    category: Optional[TransactionCategory] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 10,
) -> dict:
    """
    Return a paginated, filtered list of transactions.
    Admins see all; others see only their own.
    Supports filtering by type, category, and date range.
    Returns total count and page metadata for frontend pagination.
    """
    query = db.query(Transaction)

    # Scope by role
    if role != "admin":
        query = query.filter(Transaction.user_id == user_id)

    # Apply filters
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    # Pagination
    total = query.count()
    transactions = (
        query.order_by(Transaction.date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "data": [TransactionOut.model_validate(t) for t in transactions],
    }


def get_transaction_by_id(
    transaction_id: int,
    user_id: int,
    role: str,
    db: Session,
) -> TransactionOut:
    """
    Return a single transaction by ID.
    Non-admins receive 404 (not 403) if accessing another user's transaction
    to avoid leaking existence of records.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise NotFoundError("Transaction")

    # Hide other users' transactions from non-admins
    if role != "admin" and transaction.user_id != user_id:
        raise NotFoundError("Transaction")

    return TransactionOut.model_validate(transaction)


def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    user_id: int,
    role: str,
    db: Session,
) -> TransactionOut:
    """
    Update a transaction's fields.
    Only the owner or an admin can update a transaction.
    Only provided fields are changed.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise NotFoundError("Transaction")

    if role != "admin" and transaction.user_id != user_id:
        raise NotFoundError("Transaction")

    if payload.amount is not None:
        transaction.amount = payload.amount
    if payload.type is not None:
        transaction.type = payload.type
    if payload.category is not None:
        transaction.category = payload.category
    if payload.date is not None:
        transaction.date = payload.date
    if payload.notes is not None:
        transaction.notes = payload.notes

    db.commit()
    db.refresh(transaction)
    return TransactionOut.model_validate(transaction)


def delete_transaction(
    transaction_id: int,
    user_id: int,
    role: str,
    db: Session,
) -> dict:
    """
    Permanently delete a transaction.
    Only the owner or an admin can delete a transaction.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise NotFoundError("Transaction")

    if role != "admin" and transaction.user_id != user_id:
        raise NotFoundError("Transaction")

    db.delete(transaction)
    db.commit()
    return {"message": f"Transaction {transaction_id} deleted successfully."}