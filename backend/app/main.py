import os
import re
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import LessonProgress, User
from .schemas import (
    AuthResponse,
    Credentials,
    ProgressUpdate,
    ProgressView,
    TutorRequest,
    TutorResponse,
)
from .security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

LESSONS = [
    {
        "id": "sql-select-where",
        "title": "SELECT and WHERE",
        "subject": "SQL",
        "description": "Choose columns and filter rows with clear SQL statements.",
        "duration": "10 min",
    },
    {
        "id": "sql-joins",
        "title": "JOIN related tables",
        "subject": "SQL",
        "description": "Write INNER and LEFT JOIN statements to combine related rows.",
        "duration": "8 min",
    },
    {
        "id": "sql-group-by",
        "title": "GROUP BY summaries",
        "subject": "SQL",
        "description": "Use aggregate functions and GROUP BY to summarize query results.",
        "duration": "12 min",
    },
    {
        "id": "python-fundamentals",
        "title": "Variables and values",
        "subject": "Python",
        "description": "Work with variables, strings, numbers, and booleans in Python.",
        "duration": "10 min",
    },
    {
        "id": "python-control-flow",
        "title": "Conditions and loops",
        "subject": "Python",
        "description": "Use if statements and loops to control what your code does.",
        "duration": "12 min",
    },
    {
        "id": "python-functions",
        "title": "Functions and lists",
        "subject": "Python",
        "description": "Write reusable functions that work with lists of values.",
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


@app.post("/api/tutor/chat", response_model=TutorResponse)
async def tutor_chat(
    request: TutorRequest,
    user: User = Depends(get_current_user),
):
    del user  # Authentication is required; conversation content is not stored by this API.
    lesson = next((item for item in LESSONS if item["id"] == request.lesson_id), None)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    if request.messages[0].role != "user" or request.messages[-1].role != "user":
        raise HTTPException(status_code=422, detail="Tutor messages must start and end with a student message.")
    if any(left.role == right.role for left, right in zip(request.messages, request.messages[1:])):
        raise HTTPException(status_code=422, detail="Tutor messages must alternate between student and tutor.")

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="The tutor is not configured yet. Add OPENAI_API_KEY to the backend environment.",
        )

    instructions = (
        "You are Northstar, a supportive coding tutor. You teach only SQL statements and "
        "Python coding. For SQL, help write, read, and debug SQL statements. For Python, "
        "help write, read, and debug Python code. Do not tutor other subjects, programming "
        "languages, database administration, or unrelated requests. For an out-of-scope "
        "request, briefly say you can help only with SQL statements and Python coding, then "
        "invite a relevant question. Use clear, age-appropriate language and short steps. "
        "Guide understanding with one question or hint at a time. Be accurate and kind. Do "
        "not ask for personal details; if the student shares them, do not repeat them and "
        "gently return to the coding task.\n\n"
        f"Lesson: {lesson['title']} ({lesson['subject']}). {lesson['description']}"
    )
    input_messages = [
        {"role": message.role, "content": message.content}
        for message in request.messages
    ]

    try:
        async with AsyncOpenAI(api_key=api_key, timeout=30.0) as client:
            response = await client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
                instructions=instructions,
                input=input_messages,
                max_output_tokens=500,
                store=False,
            )
    except OpenAIError:
        raise HTTPException(
            status_code=503,
            detail="The tutor is temporarily unavailable. Please try again shortly.",
        )

    answer = response.output_text.strip()
    if not answer:
        raise HTTPException(status_code=503, detail="The tutor could not respond. Please try again.")
    return TutorResponse(message=answer)
