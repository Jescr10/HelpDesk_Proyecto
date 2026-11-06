from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.users.by_email(email.lower())
        return user if user and verify_password(password, user.password_hash) else None

    def token_for(self, user: User) -> dict[str, str]:
        return {"access_token": create_access_token(user.email, user.role), "token_type": "bearer"}
