from pydantic import BaseModel
from typing import Literal, Optional


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[Literal['teaching_office', 'evaluation_team', 'evaluation_office', 'president_office']] = None


class LoginResponse(BaseModel):
    token: str
    userId: str
    role: str
    expiresIn: int
    teachingOfficeId: str | None = None


class TokenData(BaseModel):
    username: str
    user_id: str
    role: str
