# AI Tutor Platform

A starter full-stack learning app with a React frontend and a Python FastAPI backend. The first slice supports student registration, sign-in, lesson browsing, and saving lesson progress. The tutor interaction is the next milestone.

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

The development UI talks to the backend at http://127.0.0.1:8000. Override this with `VITE_API_URL` if needed.

## What is implemented

- Student account registration and sign-in using Argon2 password hashes and short-lived signed access tokens.
- Lesson catalog served by the Python API.
- Authenticated progress read/write, stored in a local SQLite database for development.
- A responsive React dashboard with lesson progress and completion actions.

## Current boundaries

This is a development starter. It is not ready for production use. Before deployment, configure a production database, HTTPS, secure cookie/session strategy, account recovery, rate limits, migrations, privacy/retention controls, and deployment secrets. The tutor model integration is not wired yet; do not put provider keys in the frontend.

## Project layout

- `frontend/`: React + Vite web app.
- `backend/`: FastAPI API, SQLAlchemy models, and SQLite development storage.
- `docs/`: product notes and the initial junior-developer game plan.
