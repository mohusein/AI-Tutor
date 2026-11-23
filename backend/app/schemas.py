from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=10, max_length=128)


class UserView(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserView


class ProgressUpdate(BaseModel):
    completed: bool
    last_position: int = Field(default=0, ge=0)


class ProgressView(BaseModel):
    lesson_id: str
    completed: bool
    last_position: int

    model_config = ConfigDict(from_attributes=True)


class TutorMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class TutorRequest(BaseModel):
    lesson_id: str = Field(min_length=1, max_length=100)
    messages: list[TutorMessage] = Field(min_length=1, max_length=12)


class TutorResponse(BaseModel):
    message: str
