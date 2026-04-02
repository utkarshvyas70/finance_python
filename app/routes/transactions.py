from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import TransactionCategory, TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionOut, TransactionUpdate
from app.services import transaction_service
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/",
    response_model=TransactionOut,
    status_code=201,
    summary="Create a new transaction",
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.create_transaction(payload, current_user.id, db)


@router.get(
    "/",
    summary="List transactions with optional filters and pagination",
)
def list_transactions(
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    category: Optional[TransactionCategory] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Filter from this date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Filter up to this date (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.get_all_transactions(
        db=db,
        user_id=current_user.id,
        role=current_user.role.value,
        type=type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Get a single transaction by ID",
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.get_transaction_by_id(
        transaction_id, current_user.id, current_user.role.value, db
    )


@router.put(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Update a transaction",
)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.update_transaction(
        transaction_id, payload, current_user.id, current_user.role.value, db
    )


@router.delete(
    "/{transaction_id}",
    summary="Delete a transaction",
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.delete_transaction(
        transaction_id, current_user.id, current_user.role.value, db
    )