# 💰 Finance Tracker API

A production-style REST API backend for managing and analyzing personal financial records.
Built with **FastAPI**, **SQLAlchemy ORM**, and **SQLite** — following clean layered architecture.

---

## 🚀 Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Framework      | FastAPI 0.115                     |
| Database       | SQLite                            |
| ORM            | SQLAlchemy 2.0                    |
| Validation     | Pydantic v2                       |
| Authentication | JWT (python-jose) + bcrypt        |
| API Docs       | Swagger UI (auto-generated)       |
| Server         | Uvicorn (ASGI)                    |

---

## 📁 Folder Structure
```
finance-tracker/
├── main.py                        ← App factory, middleware, OpenAPI config
├── seed.py                        ← Populate DB with realistic dummy data
├── requirements.txt               ← All dependencies
├── .env.example                   ← Environment variable template
├── .gitignore
└── app/
    ├── config.py                  ← Pydantic settings (reads from .env)
    ├── database.py                ← SQLAlchemy engine, session, Base, get_db()
    │
    ├── models/                    ← SQLAlchemy ORM models (DB tables)
    │   ├── user.py                ← User table + UserRole enum
    │   └── transaction.py         ← Transaction table + type/category enums
    │
    ├── schemas/                   ← Pydantic request/response schemas
    │   ├── auth.py                ← LoginRequest, TokenOut
    │   ├── user.py                ← UserCreate, UserUpdate, UserOut
    │   ├── transaction.py         ← TransactionCreate, TransactionOut, FinancialSummary
    │   └── common.py              ← Shared base schemas
    │
    ├── services/                  ← Business logic layer (no DB calls in routes)
    │   ├── auth_service.py        ← register_user(), login_user()
    │   ├── user_service.py        ← CRUD operations for users
    │   ├── transaction_service.py ← CRUD + filters + pagination
    │   └── analytics_service.py  ← Aggregations, summaries, monthly reports
    │
    ├── routes/                    ← FastAPI route handlers (thin layer)
    │   ├── health.py              ← GET /health
    │   ├── auth.py                ← /register, /login, /me
    │   ├── users.py               ← CRUD /users (admin only)
    │   ├── transactions.py        ← CRUD /transactions
    │   └── analytics.py           ← /summary, /category-breakdown, /monthly, /recent
    │
    └── utils/                     ← Shared utilities
        ├── security.py            ← JWT creation/decoding, password hashing
        ├── dependencies.py        ← get_current_user, require_role()
        ├── exceptions.py          ← Custom HTTP exceptions + global handler
        └── responses.py           ← Consistent success/error envelope helpers
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd finance-tracker
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
```

`.env` file contents:
```env
APP_NAME="Finance Tracker API"
APP_VERSION="1.0.0"
DEBUG=true
DATABASE_URL="sqlite:///./finance_tracker.db"
SECRET_KEY="change-me-before-deploying"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Seed the database
```bash
python seed.py
```

This creates 3 users and 30 transactions each across 6 months (Oct 2025 – Mar 2026).

### 6. Start the server
```bash
uvicorn main:app --reload
```

### 7. Open API documentation
```
http://localhost:8000/docs
```

---

## 🔐 Authentication

All protected routes require a Bearer JWT token.

**Step 1 — Login:**
```
POST /api/v1/auth/login
```
```json
{
  "email": "utkarsh@example.com",
  "password": "test123"
}
```

**Step 2 — Copy the `access_token` from response.**

**Step 3 — In Swagger UI:**
Click **🔒 Authorize** → paste token in **BearerAuth** field → click **Authorize**.

---

## 👥 Test Credentials (after seeding)

| Role     | Email                   | Password |
|----------|-------------------------|----------|
| Admin    | utkarsh@example.com     | test123  |
| Analyst  | analyst@example.com     | test123  |
| Viewer   | viewer@example.com      | test123  |

---

## 🔑 Role Based Access Control

| Action                        | Viewer | Analyst | Admin |
|-------------------------------|--------|---------|-------|
| View own transactions         | ✅     | ✅      | ✅    |
| Filter + paginate transactions| ✅     | ✅      | ✅    |
| View analytics/summary        | ✅     | ✅      | ✅    |
| Create transactions           | ✅     | ✅      | ✅    |
| Update/delete own transaction | ✅     | ✅      | ✅    |
| View all users' data          | ❌     | ❌      | ✅    |
| Manage users (CRUD)           | ❌     | ❌      | ✅    |
| Update/delete any transaction | ❌     | ❌      | ✅    |

---

## 📡 API Endpoints

### Health
| Method | Endpoint           | Auth | Description     |
|--------|--------------------|------|-----------------|
| GET    | /api/v1/health     | ❌   | Health check    |

### Auth
| Method | Endpoint                | Auth | Description              |
|--------|-------------------------|------|--------------------------|
| POST   | /api/v1/auth/register   | ❌   | Register new user        |
| POST   | /api/v1/auth/login      | ❌   | Login, receive JWT token |
| GET    | /api/v1/auth/me         | ✅   | Get current user info    |

### Users (Admin only)
| Method | Endpoint                | Auth | Description        |
|--------|-------------------------|------|--------------------|
| POST   | /api/v1/users/          | ✅   | Create user        |
| GET    | /api/v1/users/          | ✅   | List all users     |
| GET    | /api/v1/users/{id}      | ✅   | Get user by ID     |
| PATCH  | /api/v1/users/{id}      | ✅   | Update user        |
| DELETE | /api/v1/users/{id}      | ✅   | Delete user        |

### Transactions
| Method | Endpoint                        | Auth | Description                      |
|--------|---------------------------------|------|----------------------------------|
| POST   | /api/v1/transactions/           | ✅   | Create transaction               |
| GET    | /api/v1/transactions/           | ✅   | List with filters + pagination   |
| GET    | /api/v1/transactions/{id}       | ✅   | Get transaction by ID            |
| PUT    | /api/v1/transactions/{id}       | ✅   | Update transaction               |
| DELETE | /api/v1/transactions/{id}       | ✅   | Delete transaction               |

**Query parameters for GET /transactions:**
| Param       | Type     | Example                    | Description              |
|-------------|----------|----------------------------|--------------------------|
| type        | string   | income / expense           | Filter by type           |
| category    | string   | salary / food / rent       | Filter by category       |
| start_date  | datetime | 2026-01-01T00:00:00        | Filter from date         |
| end_date    | datetime | 2026-03-31T00:00:00        | Filter to date           |
| page        | integer  | 1                          | Page number              |
| limit       | integer  | 10                         | Results per page (max 100)|

### Analytics
| Method | Endpoint                              | Auth | Description                     |
|--------|---------------------------------------|------|---------------------------------|
| GET    | /api/v1/analytics/summary             | ✅   | Full financial summary          |
| GET    | /api/v1/analytics/category-breakdown  | ✅   | Spending grouped by category    |
| GET    | /api/v1/analytics/monthly             | ✅   | Month-by-month income/expense   |
| GET    | /api/v1/analytics/recent              | ✅   | Last N transactions             |

---

## 📨 Sample Requests & Responses

### Register
**Request:**
```json
POST /api/v1/auth/register
{
  "full_name": "Utkarsh Vyas",
  "email": "utkarsh@example.com",
  "password": "test123",
  "role": "admin"
}
```
**Response `201`:**
```json
{
  "id": 1,
  "full_name": "Utkarsh Vyas",
  "email": "utkarsh@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-04-01T00:00:00"
}
```

### Create Transaction
**Request:**
```json
POST /api/v1/transactions/
{
  "amount": 50000.00,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01T00:00:00",
  "notes": "April salary"
}
```
**Response `201`:**
```json
{
  "id": 1,
  "amount": 50000.0,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01T00:00:00",
  "notes": "April salary",
  "user_id": 1,
  "created_at": "2026-04-01T10:00:00"
}
```

### Financial Summary
**Response `200`:**
```json
{
  "total_income": 315000.00,
  "total_expense": 48500.00,
  "current_balance": 266500.00,
  "total_transactions": 30,
  "category_breakdown": [
    { "category": "salary",     "total": 285000.00, "count": 6 },
    { "category": "rent",       "total": 12000.00,  "count": 1 },
    { "category": "food",       "total": 8500.00,   "count": 5 }
  ],
  "monthly_totals": [
    { "month": "2025-10", "income": 52000.00, "expense": 9200.00, "net": 42800.00 },
    { "month": "2025-11", "income": 48000.00, "expense": 7800.00, "net": 40200.00 },
    { "month": "2025-12", "income": 55000.00, "expense": 8100.00, "net": 46900.00 }
  ]
}
```

### Error Responses

**400 Bad Request:**
```json
{ "detail": "A user with this email already exists." }
```

**401 Unauthorized:**
```json
{ "detail": "Invalid or expired token." }
```

**403 Forbidden:**
```json
{ "detail": "Access denied. Required role(s): ['admin']" }
```

**404 Not Found:**
```json
{ "detail": "Transaction not found." }
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "Amount must be greater than zero.",
      "type": "value_error"
    }
  ]
}
```

---

## 🧪 How to Test

### Using Swagger UI (Recommended)
1. Run `uvicorn main:app --reload`
2. Open `http://localhost:8000/docs`
3. Register or login to get a token
4. Click **🔒 Authorize** → paste token → **Authorize**
5. Test any endpoint with **Try it out** → **Execute**

### Using Postman
1. Import base URL: `http://localhost:8000`
2. Add header: `Authorization: Bearer <your_token>`
3. Set body to `raw → JSON`
4. Hit any endpoint

### Quick test sequence
```
1. POST /api/v1/auth/login        → get token
2. GET  /api/v1/auth/me           → verify identity
3. POST /api/v1/transactions/     → create transaction
4. GET  /api/v1/transactions/     → list with filters
5. GET  /api/v1/analytics/summary → see financial summary
6. GET  /api/v1/analytics/monthly → see monthly breakdown
```

---

## 📝 Assumptions Made

1. **SQLite** used for simplicity — swap to PostgreSQL by changing `DATABASE_URL` in `.env`
2. **Amounts are always positive** — `type` field (`income`/`expense`) determines direction
3. **Non-admin users** can only view and manage their own transactions
4. **Soft delete not implemented** — all deletes are permanent
5. **Password minimum** is 6 characters
6. **Token expiry** is 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`)
7. **Categories are fixed enums** — ensures consistency across analytics queries
8. **Seed data spans 6 months** (Oct 2025 – Mar 2026) with guaranteed monthly salaries
9. **Pagination default** is page 1, limit 10, max 100 per page

---

## 🏗️ Architecture Decisions

| Decision | Reason |
|---|---|
| Layered architecture (routes → services → models) | Separation of concerns, easy to test each layer |
| Pydantic v2 schemas separate from ORM models | Decouples DB layer from API contract |
| JWT stored client-side | Stateless auth, no session storage needed |
| `require_role()` as reusable dependency | Applied per-route, composable, clean |
| `HTTPBearer` over `OAuth2PasswordBearer` | Fixes Swagger UI authorize box |
| SQLAlchemy `func.strftime` for monthly grouping | Native SQLite aggregation, no Python loops |
| Global exception handler | All 500s return clean JSON, never plain text |