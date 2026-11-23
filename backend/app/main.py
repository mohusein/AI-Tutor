import os
import re
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import LessonProgress, User
from .schemas import AuthResponse, Credentials, ProgressUpdate, ProgressView
from .security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

LESSONS = [
    {
        "id": "linear-equations",
        "title": "Solving linear equations",
        "subject": "Algebra",
        "description": "Learn to isolate a variable using inverse operations.",
        "duration": "10 min",
    },
    {
        "id": "expressions",
        "title": "Simplifying expressions",
        "subject": "Algebra",
        "description": "Combine like terms and use the distributive property.",
        "duration": "8 min",
    },
    {
        "id": "fractions",
        "title": "Fractions and ratios",
        "subject": "Math",
        "description": "Build confidence with equivalent fractions and ratios.",
        "duration": "12 min",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AI Tutor API", version="0.1.0", lifespan=lifespan)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/lessons")
def list_lessons():
    return LESSONS


def validate_email(email: str) -> str:
    normalized = email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    return normalized


@app.post("/api/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(credentials: Credentials, db: Session = Depends(get_db)):
    email = validate_email(credentials.email)
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(email=email, password_hash=hash_password(credentials.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.id), user=user)


@app.post("/api/auth/login", response_model=AuthResponse)
def login(credentials: Credentials, db: Session = Depends(get_db)):
    email = validate_email(credentials.email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return AuthResponse(access_token=create_access_token(user.id), user=user)


@app.get("/api/progress", response_model=list[ProgressView])
def get_progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list(db.scalars(select(LessonProgress).where(LessonProgress.user_id == user.id)))


@app.put("/api/progress/{lesson_id}", response_model=ProgressView)
def save_progress(
    lesson_id: str,
    update: ProgressUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesson = next((item for item in LESSONS if item["id"] == lesson_id), None)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    progress = db.scalar(
        select(LessonProgress).where(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    if progress is None:
        progress = LessonProgress(user_id=user.id, lesson_id=lesson_id)
        db.add(progress)

    progress.completed = update.completed
    progress.last_position = update.last_position
    db.commit()
    db.refresh(progress)
    return progress
