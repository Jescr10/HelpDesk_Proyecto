from app.core.time import utcnow
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Comment, History, Ticket, User
from app.models.enums import STATUSES
from app.repositories.tickets import TicketRepository
from app.repositories.users import UserRepository
from app.schemas.tickets import AssignIn, CommentIn, StatusIn, TicketIn


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.tickets = TicketRepository(db)
        self.users = UserRepository(db)

    def serialize(self, ticket: Ticket) -> dict:
        comments = [{"id": item.id, "body": item.body, "author": item.author.name, "created_at": item.created_at} for item in self.tickets.comments_for(ticket.id)]
        history = [{"id": item.id, "event_type": item.event_type, "detail": item.detail, "actor": item.actor.name, "created_at": item.created_at} for item in self.tickets.history_for(ticket.id)]
        return {"id": ticket.id, "title": ticket.title, "description": ticket.description, "category": ticket.category, "priority": ticket.priority, "status": ticket.status, "requester_id": ticket.requester_id, "assignee_id": ticket.assignee_id, "requester": ticket.requester.name, "assignee": ticket.assignee.name if ticket.assignee else None, "created_at": ticket.created_at, "due_at": ticket.due_at, "overdue": ticket.due_at < utcnow() and ticket.status not in ("Resolved", "Closed", "Cancelled"), "comments": comments, "history": history}

    def _ticket(self, ticket_id: int) -> Ticket:
        ticket = self.tickets.by_id(ticket_id)
        if not ticket:
            raise HTTPException(404, "Ticket not found")
        return ticket

    @staticmethod
    def _assert_owner(ticket: Ticket, user: User) -> None:
        if user.role == "requester" and ticket.requester_id != user.id:
            raise HTTPException(403, "Ticket unavailable")

    def _event(self, ticket: Ticket, actor: User, kind: str, detail: str) -> None:
        self.db.add(History(ticket_id=ticket.id, actor_id=actor.id, event_type=kind, detail=detail))
        self.db.commit()

    def create(self, body: TicketIn, user: User) -> dict:
        hours = {"Low": 72, "Medium": 48, "High": 24, "Critical": 4}.get(body.priority, 48)
        ticket = Ticket(**body.model_dump(), requester_id=user.id, due_at=utcnow() + timedelta(hours=hours))
        self.db.add(ticket)
        self.db.flush()
        self._event(ticket, user, "created", "Ticket created")
        return self.serialize(ticket)

    def list(self, user: User, status_filter: str | None, category: str | None, priority: str | None) -> dict:
        requester_id = user.id if user.role == "requester" else None
        return {"items": [self.serialize(ticket) for ticket in self.tickets.list(requester_id=requester_id, status=status_filter, category=category, priority=priority)]}

    def detail(self, ticket_id: int, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        self._assert_owner(ticket, user)
        return self.serialize(ticket)

    def history(self, ticket_id: int, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        self._assert_owner(ticket, user)
        return {"items": [{"id": item.id, "event_type": item.event_type, "detail": item.detail, "actor": item.actor.name, "created_at": item.created_at} for item in self.tickets.history_for(ticket.id)]}

    def update(self, ticket_id: int, body: TicketIn, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        self._assert_owner(ticket, user)
        if user.role == "requester" and ticket.status != "Open":
            raise HTTPException(403, "Only open tickets can be edited")
        if ticket.status in ("Closed", "Cancelled"):
            raise HTTPException(409, "El ticket ya estÃ¡ finalizado")
        if ticket.priority != body.priority:
            ticket.due_at = ticket.created_at + timedelta(hours={"Low": 72, "Medium": 48, "High": 24, "Critical": 4}[body.priority])
        for field, value in body.model_dump().items():
            setattr(ticket, field, value)
        self._event(ticket, user, "updated", "Ticket updated")
        return self.serialize(ticket)

    def assign(self, ticket_id: int, body: AssignIn, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        assignee = self.users.by_id(body.assignee_id)
        if not assignee:
            raise HTTPException(404, "Ticket or assignee not found")
        if assignee.role not in ("technician", "supervisor"):
            raise HTTPException(422, "Assignee must be a technician or supervisor")
        ticket.assignee = assignee
        self._event(ticket, user, "assigned", f"Assigned to {assignee.name}")
        return self.serialize(ticket)

    def change_status(self, ticket_id: int, body: StatusIn, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        if body.status not in STATUSES:
            raise HTTPException(422, "Unknown status")
        allowed = {"Open": {"In Progress", "Cancelled"}, "In Progress": {"Open", "Resolved", "Cancelled"}, "Resolved": {"In Progress", "Closed"}, "Closed": set(), "Cancelled": set()}
        if body.status not in allowed[ticket.status]:
            raise HTTPException(409, "TransiciÃ³n de estado no permitida")
        ticket.status = body.status
        self._event(ticket, user, "status_changed", body.status)
        return self.serialize(ticket)

    def cancel(self, ticket_id: int, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        self._assert_owner(ticket, user)
        if ticket.status not in ("Open", "In Progress"):
            raise HTTPException(409, "Solo puedes cancelar tickets activos")
        ticket.status = "Cancelled"
        self._event(ticket, user, "cancelled", "Ticket cancelled")
        return self.serialize(ticket)

    def close(self, ticket_id: int, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        if ticket.status != "Resolved":
            raise HTTPException(409, "Resuelve el ticket antes de cerrarlo")
        ticket.status = "Closed"
        self._event(ticket, user, "closed", "Ticket closed")
        return self.serialize(ticket)

    def comment(self, ticket_id: int, body: CommentIn, user: User) -> dict:
        ticket = self._ticket(ticket_id)
        self._assert_owner(ticket, user)
        comment = Comment(ticket_id=ticket.id, author_id=user.id, body=body.body)
        self.db.add(comment)
        self.db.flush()
        self._event(ticket, user, "commented", "Comment added")
        return {"id": comment.id, "body": comment.body}

    def dashboard(self, user: User) -> dict:
        tickets = self.tickets.list(requester_id=user.id if user.role == "requester" else None)
        group = lambda attr: {str(key): sum(1 for ticket in tickets if getattr(ticket, attr) == key) for key in set(getattr(ticket, attr) for ticket in tickets)}
        return {"open": sum(ticket.status not in ("Resolved", "Closed", "Cancelled") for ticket in tickets), "overdue": sum(ticket.due_at < utcnow() and ticket.status not in ("Resolved", "Closed", "Cancelled") for ticket in tickets), "status": group("status"), "priority": group("priority"), "category": group("category"), "workload": {str(key): sum(1 for ticket in tickets if ticket.assignee_id == key) for key in set(ticket.assignee_id for ticket in tickets if ticket.assignee_id)}}