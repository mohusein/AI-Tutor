# AI Tutor Platform

A starter full-stack learning app with a React frontend and a Python FastAPI backend. Students create separate accounts and can save their own progress. Tutoring is limited to SQL statements and Python coding.

## Requirements

- Node.js 20+
- Python 3.11+

## Run locally

### Backend

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Replace SECRET_KEY in .env with a random secret before running.
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000 and its OpenAPI page is at http://127.0.0.1:8000/docs.

### Frontend

In a second terminal:

```sh
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (normally http://localhost:5173).

The development UI talks to the backend at http://127.0.0.1:8000. Override this with `VITE_API_URL` if needed. Set `OPENAI_API_KEY` in `backend/.env` to enable tutor replies; the key stays on the backend.

## What is implemented

- Self-service student accounts with unique email addresses, Argon2 password hashes, and short-lived signed access tokens. Each student has their own progress records; there are no shared classroom credentials.
- Lesson catalog served by the Python API.
- Starter lessons for SQL SELECT/WHERE, JOIN, GROUP BY, and Python variables, control flow, and functions.
- Authenticated progress read/write, stored in a local SQLite database for development.
- A responsive React dashboard with lesson progress and completion actions.
- Authenticated lesson-scoped tutor chat through the OpenAI Responses API, instructed to stay within SQL statements and Python coding. Chat history stays in the browser session and is not saved in the app database.

## Current boundaries

This is a development starter. It is not ready for production use. Before deployment, configure a production database, HTTPS, secure cookie/session strategy, account recovery, rate limits, migrations, privacy/retention controls, and deployment secrets. Tutor messages are sent to OpenAI to generate a reply; add the required user-facing privacy notice and review provider data settings before serving students. Never put provider keys in the frontend.

## Project layout

- `frontend/`: React + Vite web app.
- `backend/`: FastAPI API, SQLAlchemy models, and SQLite development storage.
- `docs/`: product notes and the initial junior-developer game plan.
