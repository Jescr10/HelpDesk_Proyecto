"""La persona de soporte asignada administra; los lectores del ticket consultan."""

from __future__ import annotations

from app.domain.errors import NotFoundError, PermissionDeniedError, ValidationError
from app.models.entities import User
from app.models.tasks import TareaTicket
from app.repositories.tasks import TaskRepository
from app.services.tickets import TicketService


class TaskService:
    def __init__(self, repository: TaskRepository, tickets: TicketService):
        self.repository = repository
        self.tickets = tickets

    def list(self, actor: User, ticket_id: int) -> list[TareaTicket]:
        self.tickets.require_for(actor, ticket_id)
        return self.repository.list(ticket_id)

    def _authorize_write(self, actor: User, ticket_id: int) -> None:
        ticket = self.tickets.require_for(actor, ticket_id)
        if not actor.is_staff or actor.id != ticket.assignee_id:
            raise PermissionDeniedError("Only assigned support staff can manage tasks")
        if not ticket.is_open:
            raise ValidationError("ticket is closed or cancelled", field="ticket")

    def add(self, actor: User, ticket_id: int, descripcion: str) -> TareaTicket:
        self._authorize_write(actor, ticket_id)
        descripcion = descripcion.strip()
        if not 1 <= len(descripcion) <= 500:
            raise ValidationError("Escribe una tarea de entre 1 y 500 caracteres.", field="descripcion")
        return self.repository.add(TareaTicket(ticket_id=ticket_id, descripcion=descripcion))

    def complete(self, actor: User, ticket_id: int, task_id: int) -> TareaTicket:
        self._authorize_write(actor, ticket_id)
        task = self.repository.by_id(ticket_id, task_id)
        if task is None:
            raise NotFoundError("task", task_id)
        # Idempotente: repetir la petición nunca vuelve a dejarla pendiente.
        return task if task.completada else self.repository.complete(task)
