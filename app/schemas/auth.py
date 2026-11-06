from typing import Literal
from pydantic import EmailStr, Field
from app.schemas.base import InputModel

class Login(InputModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserIn(InputModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    role: Literal["requester", "technician", "supervisor", "administrator"] = "requester"
    password: str = Field(min_length=10, max_length=128)
