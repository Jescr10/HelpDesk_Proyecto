"""Crea un administrador con contraseña interactiva, sin credenciales predeterminadas."""
from getpass import getpass
from sqlalchemy import select
from app.core.config import settings
from app.core.database import create_session_factory
from app.core.security import hash_password
from app.models import User
from app.schemas.auth import UserIn

def main():
    email = input("Correo: ").strip().lower()
    name = input("Nombre: ").strip()
    password = getpass("Contraseña (mínimo 10 caracteres): ")
    if password != getpass("Confirma la contraseña: "):
        raise SystemExit("Las contraseñas no coinciden")
    data = UserIn(email=email, name=name, password=password, role="administrator")
    with create_session_factory(settings.database_url)() as db:
        if db.scalar(select(User).where(User.email == email)):
            raise SystemExit("El correo ya está registrado")
        db.add(User(email=email, name=data.name, role=data.role, password_hash=hash_password(data.password)))
        db.commit()
    print("Administrador creado")

if __name__ == "__main__":
    main()
