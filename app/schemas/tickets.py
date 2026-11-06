from typing import Literal
from pydantic import Field
from app.schemas.base import InputModel

Category = Literal["General", "Hardware", "Software", "Network"]
Priority = Literal["Low", "Medium", "High", "Critical"]
Status = Literal["Open", "In Progress", "Resolved", "Closed", "Cancelled"]

class TicketIn(InputModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=10000)
    category: Category = "General"
    priority: Priority = "Medium"

class StatusIn(InputModel):
    status: Status

class AssignIn(InputModel):
    assignee_id: int = Field(gt=0)

class CommentIn(InputModel):
    body: str = Field(min_length=1, max_length=5000)
