from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.auth import UserIn
from app.core.security import hash_password

from app.core.database import get_db
from app.core.dependencies import current_user, require_roles
from app.models import User
from app.repositories.users import UserRepository

router = APIRouter()


@router.get("/api/users/me")
def me(user: Annotated[User, Depends(current_user)]) -> dict:
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


@router.get("/api/users")
def users(_: Annotated[User, Depends(require_roles("administrator", "supervisor"))], db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    return [{"id": user.id, "email": user.email, "name": user.name, "role": user.role} for user in UserRepository(db).all()]


@router.get("/api/catalogs")
def catalogs(_: Annotated[User, Depends(current_user)]) -> dict:
    return {"categories": ["General", "Hardware", "Software", "Network"], "priorities": ["Low", "Medium", "High", "Critical"], "statuses": ["Open", "In Progress", "Resolved", "Closed", "Cancelled"]}

@router.get("/api/assignees")
def assignees(_: Annotated[User, Depends(require_roles("technician", "supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    return [{"id": u.id, "name": u.name} for u in UserRepository(db).all() if u.role in ("technician", "supervisor")]


@router.post("/api/users", status_code=201)
def create_user(body: UserIn, _: Annotated[User, Depends(require_roles("administrator"))], db: Annotated[Session, Depends(get_db)]) -> dict:
    user = User(email=str(body.email).lower(), name=body.name, role=body.role, password_hash=hash_password(body.password))
    try:
        UserRepository(db).add(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El correo ya está registrado")
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
