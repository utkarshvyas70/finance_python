"""
Seed script — populates the database with realistic dummy data.
Run with: python seed.py
"""

from datetime import datetime, timedelta
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import User, Transaction
from app.models.user import UserRole
from app.models.transaction import TransactionType, TransactionCategory
from app.database import Base
from app.utils.security import hash_password

# ── Helpers ──────────────────────────────────────────────────────────

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


# ── Seed data ─────────────────────────────────────────────────────────

USERS = [
    {
        "full_name": "Utkarsh Vyas",
        "email": "utkarsh@example.com",
        "password": "test123",
        "role": UserRole.admin,
    },
    {
        "full_name": "Analyst User",
        "email": "analyst@example.com",
        "password": "test123",
        "role": UserRole.analyst,
    },
    {
        "full_name": "Viewer User",
        "email": "viewer@example.com",
        "password": "test123",
        "role": UserRole.viewer,
    },
]

INCOME_TEMPLATES = [
    {"category": TransactionCategory.salary,     "amount_range": (45000, 55000), "notes": "Monthly salary credit"},
    {"category": TransactionCategory.freelance,  "amount_range": (5000,  15000), "notes": "Freelance project payment"},
    {"category": TransactionCategory.investment, "amount_range": (1000,  8000),  "notes": "Investment returns"},
]

EXPENSE_TEMPLATES = [
    {"category": TransactionCategory.food,          "amount_range": (500,  2000),  "notes": "Food and groceries"},
    {"category": TransactionCategory.transport,     "amount_range": (300,  1500),  "notes": "Transport expenses"},
    {"category": TransactionCategory.utilities,     "amount_range": (800,  2500),  "notes": "Utility bills"},
    {"category": TransactionCategory.healthcare,    "amount_range": (500,  3000),  "notes": "Healthcare expenses"},
    {"category": TransactionCategory.entertainment, "amount_range": (300,  1500),  "notes": "Entertainment and outings"},
    {"category": TransactionCategory.education,     "amount_range": (1000, 5000),  "notes": "Online courses and books"},
    {"category": TransactionCategory.shopping,      "amount_range": (500,  4000),  "notes": "Shopping expenses"},
    {"category": TransactionCategory.rent,          "amount_range": (8000, 15000), "notes": "Monthly rent"},
]


def generate_transactions(user_id: int, count: int = 30) -> list:
    transactions = []
    start_date = datetime(2025, 10, 1)
    end_date   = datetime(2026, 3, 31)

    # Guarantee at least 1 salary per month
    for month_offset in range(6):
        month_date = datetime(2025, 10, 1) + timedelta(days=30 * month_offset)
        salary = INCOME_TEMPLATES[0]
        transactions.append(Transaction(
            amount=round(random.uniform(*salary["amount_range"]), 2),
            type=TransactionType.income,
            category=salary["category"],
            date=month_date.replace(day=1),
            notes=salary["notes"],
            user_id=user_id,
        ))

    # Fill remaining with random income/expenses
    for _ in range(count - 6):
        is_income = random.random() < 0.25  # 25% chance income, 75% expense
        if is_income:
            template = random.choice(INCOME_TEMPLATES[1:])  # skip salary
            tx_type  = TransactionType.income
        else:
            template = random.choice(EXPENSE_TEMPLATES)
            tx_type  = TransactionType.expense

        transactions.append(Transaction(
            amount=round(random.uniform(*template["amount_range"]), 2),
            type=tx_type,
            category=template["category"],
            date=random_date(start_date, end_date),
            notes=template["notes"],
            user_id=user_id,
        ))

    return transactions


# ── Main ──────────────────────────────────────────────────────────────

def seed():
    print("🌱 Seeding database...")

    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Transaction).delete()
        db.query(User).delete()
        db.commit()
        print("  ✓ Cleared existing data")

        # Create users
        created_users = []
        for u in USERS:
            user = User(
                full_name=u["full_name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=True,
            )
            db.add(user)
            db.flush()  # get user.id before commit
            created_users.append(user)
            print(f"  ✓ Created user: {u['email']} ({u['role'].value})")

        db.commit()

        # Create transactions for each user
        for user in created_users:
            transactions = generate_transactions(user.id, count=30)
            for tx in transactions:
                db.add(tx)
            db.commit()
            print(f"  ✓ Added 30 transactions for {user.email}")

        print("\n✅ Seed complete!")
        print("\n── Login credentials ───────────────────────────")
        print("  Admin    → utkarsh@example.com  / test123")
        print("  Analyst  → analyst@example.com  / test123")
        print("  Viewer   → viewer@example.com   / test123")
        print("────────────────────────────────────────────────")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()