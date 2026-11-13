"""Demostración local aislada: python -m app.scripts.tasks_demo prepare|serve.

Lee TEST_DATABASE_URL para obtener conexión, pero SIEMPRE usa la base
helpdesk_tasks_demo_test. No borra bases ni migra la base habitual.
"""

import argparse
import os
from pathlib import Path
import secrets

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

DEMO_DATABASE = "helpdesk_tasks_demo_test"
DEMO_PASSWORD = "TareasDemo2026!"


def demo_url():
    source = os.environ.get("TEST_DATABASE_URL")
    if not source:
        raise SystemExit("Define TEST_DATABASE_URL (puedes cargar .env con uv run --env-file .env).")
    return make_url(source).set(database=DEMO_DATABASE)


def prepare(url):
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as connection:
            exists = connection.scalar(text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": DEMO_DATABASE})
            if not exists:
                connection.exec_driver_sql('CREATE DATABASE "helpdesk_tasks_demo_test"')
    finally:
        admin.dispose()
    from app.core.database import create_app_engine
    from app.core.security import hash_password

    engine = create_app_engine(url)
    try:
        with engine.connect() as connection:
            initialized = connection.scalar(text("SELECT to_regclass('public.users')"))
            tasks = connection.scalar(text("SELECT to_regclass('public.ticket_tasks')"))
        if initialized:
            if not tasks:
                raise SystemExit("La base demo ya existe sin ticket_tasks. No se modificó; utiliza una base demo nueva revisada.")
            print("La demo ya existe; se conservaron todos sus datos.")
            return
        sql_dir = Path(__file__).resolve().parents[2] / "docs" / "database"
        raw = engine.raw_connection()
        try:
            for name in ("database.sql", "functions_triggers.sql", "seed.sql"):
                raw.cursor().execute((sql_dir / name).read_text(encoding="utf-8"))
            raw.commit()
        except Exception:
            raw.rollback()
            raise
        finally:
            raw.close()
        with engine.begin() as connection:
            connection.execute(text("UPDATE users SET password_hash=:hash"), {"hash": hash_password(DEMO_PASSWORD)})
        print("Demo preparada en helpdesk_tasks_demo_test. La base habitual no se modificó.")
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "serve"))
    args = parser.parse_args()
    url = demo_url()
    if args.action == "prepare":
        prepare(url)
    else:
        os.environ["DATABASE_URL"] = url.render_as_string(hide_password=False)
        os.environ["SECRET_KEY"] = secrets.token_urlsafe(48)
        os.environ["APP_NAME"] = "HelpDesk EDU · Demo de tareas"
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=8001)


if __name__ == "__main__":
    main()
