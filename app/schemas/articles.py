from pydantic import Field
from app.schemas.base import InputModel
from app.schemas.tickets import Category

class ArticleIn(InputModel):
    title: str = Field(min_length=3, max_length=160)
    body: str = Field(min_length=10, max_length=20000)
    category: Category = "General"
