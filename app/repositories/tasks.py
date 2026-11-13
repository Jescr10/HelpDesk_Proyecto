"""Persistencia de tareas; la unidad de trabajo de la petición hace el commit."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from sqlalchemy import CheckConstraint, ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.tasks import TareaTicket
from app.repositories.sqlalchemy import Base, TicketORM


class TareaTicketORM(Base):
    __tablename__ = "ticket_tasks"
    __table_args__ = (CheckConstraint("length(trim(descripcion)) > 0", name="task_description_not_blank"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    descripcion: Mapped[str] = mapped_column(String(500))
    completada: Mapped[bool] = mapped_column(default=False)
    fecha_creacion: Mapped[datetime]
    ticket: Mapped[TicketORM] = relationship()


class TaskRepository(Protocol):
    def add(self, task: TareaTicket) -> TareaTicket: ...
    def list(self, ticket_id: int) -> list[TareaTicket]: ...
    def by_id(self, ticket_id: int, task_id: int) -> TareaTicket | None: ...
    def complete(self, task: TareaTicket) -> TareaTicket: ...


def _entity(row: TareaTicketORM) -> TareaTicket:
    return TareaTicket(id=row.id, ticket_id=row.ticket_id, descripcion=row.descripcion,
                       completada=row.completada, fecha_creacion=row.fecha_creacion)


class SqlAlchemyTaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, task: TareaTicket) -> TareaTicket:
        row = TareaTicketORM(ticket_id=task.ticket_id, descripcion=task.descripcion,
                            completada=False, fecha_creacion=task.fecha_creacion)
        self.session.add(row)
        self.session.flush()
        return _entity(row)

    def list(self, ticket_id: int) -> list[TareaTicket]:
        rows = self.session.scalars(select(TareaTicketORM).where(
            TareaTicketORM.ticket_id == ticket_id).order_by(TareaTicketORM.id))
        return [_entity(row) for row in rows]

    def by_id(self, ticket_id: int, task_id: int) -> TareaTicket | None:
        row = self.session.scalar(select(TareaTicketORM).where(
            TareaTicketORM.ticket_id == ticket_id, TareaTicketORM.id == task_id))
        return _entity(row) if row else None

    def complete(self, task: TareaTicket) -> TareaTicket:
        row = self.session.get(TareaTicketORM, task.id)
        row.completada = True
        self.session.flush()
        return _entity(row)
