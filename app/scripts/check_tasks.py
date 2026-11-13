"""Ejecuta pytest exclusivamente en helpdesk_tasks_test; requiere dependencias dev."""

import os
import sys

from sqlalchemy.engine import make_url


def main():
    source = os.environ.get("TEST_DATABASE_URL")
    if not source:
        raise SystemExit("Define TEST_DATABASE_URL antes de ejecutar las pruebas.")
    url = make_url(source).set(database="helpdesk_tasks_test")
    os.environ["TEST_DATABASE_URL"] = url.render_as_string(hide_password=False)
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
    os.environ["SECRET_KEY"] = "isolated-task-module-tests-only-0123456789"
    os.environ["REQUIRE_TEST_DATABASE"] = "1"
    import pytest
    raise SystemExit(pytest.main(sys.argv[1:] or ["-q"]))


if __name__ == "__main__":
    main()
