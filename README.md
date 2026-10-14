# Fitness Agent API

A REST API that uses Claude AI (Anthropic) to generate personalized weekly training plans for members based on their fitness profile, goals, and available equipment.

## Features

- JWT authentication (register / login)
- Member fitness profile management
- AI-powered weekly training plan generation via `claude-sonnet-4-6`
- Full CRUD for training plans
- Async FastAPI + SQLite (swappable to PostgreSQL)

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| AI | Anthropic SDK — `claude-sonnet-4-6` |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite via `aiosqlite` |
| Auth | JWT (HS256) + bcrypt |
| Validation | Pydantic v2 |
| Package manager | uv |
| CI | GitHub Actions |

## Project Structure

```
fitness-agent/
├── app/
│   ├── controllers/        # HTTP route handlers (thin layer)
│   │   ├── auth_controller.py
│   │   ├── profile_controller.py
│   │   └── plan_controller.py
│   ├── services/           # Business logic
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── plan_service.py
│   │   └── agent_service.py
│   ├── repositories/       # Database access layer
│   │   ├── user_repository.py
│   │   ├── profile_repository.py
│   │   └── plan_repository.py
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── profile.py
│   │   └── plan.py
│   ├── schemas/            # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── profile.py
│   │   └── plan.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   └── main.py
├── tests/
│   ├── controllers/        # Integration tests (HTTP client)
│   ├── services/           # Unit tests (mocked repos)
│   ├── repositories/       # Unit tests (in-memory SQLite)
│   └── models/             # ORM integrity tests
├── .github/workflows/ci.yml
├── pyproject.toml
└── .env.example
```

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- An [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
git clone <repo-url>
cd fitness-agent

uv sync --group dev
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_secret_key_here           # any long random string
DATABASE_URL=sqlite+aiosqlite:///./fitness.db
```

### Run

```bash
uv run uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Login, returns JWT token |

### Profile

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/profile` | Yes | Get own fitness profile |
| POST | `/profile` | Yes | Create or upsert profile |
| PUT | `/profile` | Yes | Update profile fields |

### Training Plans

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/plans/generate` | Yes | Generate a weekly plan via AI |
| GET | `/plans` | Yes | List all plans |
| GET | `/plans/{id}` | Yes | Get plan detail |
| DELETE | `/plans/{id}` | Yes | Delete a plan |

### Example: Generate a plan

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -F "username=you@example.com" \
  -F "password=yourpassword"

# 3. Create profile
curl -X POST http://localhost:8000/profile \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "age": 28,
    "gender": "female",
    "weight_kg": 65,
    "height_cm": 168,
    "fitness_level": "intermediate",
    "goals": "lose weight and build endurance",
    "available_days": "Monday,Wednesday,Friday,Saturday",
    "equipment": "dumbbells,resistance bands,bodyweight"
  }'

# 4. Generate weekly plan
curl -X POST http://localhost:8000/plans/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"week_start": "2026-10-14"}'
```

## Running Tests

```bash
uv run pytest tests/ -v
```

Tests use an in-memory SQLite database and mock all Anthropic API calls — no real API key needed.

## CI

GitHub Actions runs the full test suite on every push to `main` and on pull requests that are opened or set to **Ready for review**.

See `.github/workflows/ci.yml`.
