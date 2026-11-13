from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    descripcion: str = Field(min_length=1, max_length=500)

    @field_validator("descripcion")
    @classmethod
    def trim_description(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Escribe la descripción de la tarea.")
        return value.strip()


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    descripcion: str
    completada: bool
    fecha_creacion: datetime
