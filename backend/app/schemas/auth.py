from pydantic import BaseModel
from typing import Literal


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Literal['teaching_office', 'evaluation_team', 'evaluation_office', 'president_office']


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
