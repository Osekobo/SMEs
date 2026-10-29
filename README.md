# Offline Sales Automation System (USSD, SMS & M-Pesa Backend)

An asynchronous FastAPI backend built for Kenyan SMEs, integrating USSD (Africa's Talking), Inbound SMS, Facebook/Instagram Meta Leads webhooks, and Safaricom Daraja M-Pesa STK Push checkout.

## Tech Stack
- **FastAPI** (Async)
- **PostgreSQL** with **SQLAlchemy 2.0** (`asyncpg`) & **Alembic**
- **Pydantic v2**
- **Python-dotenv** / `pydantic-settings`

---

## Project Structure
```
app/
├── api/          # API Routers (ussd, sms, webhooks, mpesa, products)
├── core/         # Config, settings, security
├── db/           # Database session & base model
├── models/       # SQLAlchemy ORM models (Product, USSDSession, Lead, Order)
├── schemas/      # Pydantic validation schemas
└── services/     # External integrations (africastalking, mpesa)
```

---

## Getting Started

### 1. Prerequisites & Environment Setup
- Python 3.10+
- Docker & Docker Compose

Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```

### 2. Start PostgreSQL Database
Run Docker Compose to start PostgreSQL:
```bash
docker-compose up -d
```

### 3. Install Dependencies
Create and activate a virtual environment, then install requirements:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
# source venv/bin/activate

pip install -r requirements.txt
```

### 4. Run Alembic Migrations
Initialize or upgrade the database schema using Alembic:
```bash
alembic upgrade head
```

### 5. Start the FastAPI Server
Run the application with `uvicorn`:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive API documentation at `http://localhost:8000/docs`.
