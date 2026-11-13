"""Tarea de soporte perteneciente a un único ticket."""

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.clock import now


@dataclass
class TareaTicket:
    ticket_id: int
    descripcion: str
    id: int | None = field(default=None, kw_only=True)
    completada: bool = False
    fecha_creacion: datetime = field(default_factory=now)
