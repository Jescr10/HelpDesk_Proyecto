"""Flujo completo contra PostgreSQL aislado; no reemplaza pruebas del curso."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.repositories.tasks import SqlAlchemyTaskRepository
from tests.helpers import auth_headers


@pytest.fixture
def client(committed_db):
    with TestClient(create_app()) as client:
        yield client


@pytest.fixture
def ticket(client):
    result = client.post("/api/tickets", headers=auth_headers(5), json={
        "title": "Equipo no enciende", "description": "Revisar equipo del laboratorio",
        "category": "Hardware", "priority": "Low"})
    assert result.status_code == 201
    ticket_id = result.json()["id"]
    assert client.post(f"/api/tickets/{ticket_id}/assign", headers=auth_headers(3),
                       json={"technician_id": 3}).status_code == 200
    return ticket_id


def add(client, ticket):
    response = client.post(f"/api/tickets/{ticket}/tasks", headers=auth_headers(3),
                           json={"descripcion": "  Revisar conexiones  "})
    assert response.status_code == 201
    return response.json()


def test_create_complete_and_read_from_new_session(client, ticket, pg_engine):
    task = add(client, ticket)
    assert task["ticket_id"] == ticket
    assert task["descripcion"] == "Revisar conexiones"
    assert task["completada"] is False
    assert task["fecha_creacion"]
    with Session(pg_engine) as session:
        saved = SqlAlchemyTaskRepository(session).by_id(ticket, task["id"])
        assert saved.descripcion == "Revisar conexiones"
        assert saved.completada is False
    endpoint = f"/api/tickets/{ticket}/tasks/{task['id']}/complete"
    for _ in range(2):
        response = client.post(endpoint, headers=auth_headers(3))
        assert response.status_code == 200
        assert response.json()["completada"] is True
    with Session(pg_engine) as session:
        assert SqlAlchemyTaskRepository(session).by_id(ticket, task["id"]).completada is True
    response = client.get(f"/api/tickets/{ticket}/tasks", headers=auth_headers(5))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["completada"] is True


@pytest.mark.parametrize("actor,status", [(5, 403), (4, 404), (2, 403), (1, 403), (6, 403)])
def test_reject_unauthorized_write_without_mutation(client, ticket, actor, status):
    task = add(client, ticket)
    path = f"/api/tickets/{ticket}/tasks"
    before = client.get(path, headers=auth_headers(3)).json()
    assert client.post(path, headers=auth_headers(actor), json={"descripcion": "No permitido"}).status_code == status
    assert client.post(f"{path}/{task['id']}/complete", headers=auth_headers(actor)).status_code == status
    assert client.get(path, headers=auth_headers(3)).json() == before
    if actor == 4:
        assert client.get(path, headers=auth_headers(actor)).status_code == 404


def test_task_cannot_be_completed_under_another_ticket(client, ticket):
    task = add(client, ticket)
    other = client.post("/api/tickets", headers=auth_headers(5), json={
        "title": "Otro equipo", "description": "Otro", "category": "Hardware", "priority": "Low"}).json()["id"]
    client.post(f"/api/tickets/{other}/assign", headers=auth_headers(3), json={"technician_id": 3})
    assert client.post(f"/api/tickets/{other}/tasks/{task['id']}/complete", headers=auth_headers(3)).status_code == 404
    assert client.get(f"/api/tickets/{ticket}/tasks", headers=auth_headers(3)).json() == [task]
    assert client.get(f"/api/tickets/{other}/tasks", headers=auth_headers(3)).json() == []


@pytest.mark.parametrize("body", [{"descripcion": "   "}, {"descripcion": "x" * 501}, {},
                                  {"descripcion": "Actividad", "completada": True}])
def test_invalid_input_does_not_create_task(client, ticket, body):
    path = f"/api/tickets/{ticket}/tasks"
    assert client.post(path, headers=auth_headers(3), json=body).status_code == 422
    assert client.get(path, headers=auth_headers(3)).json() == []


def test_closed_ticket_and_missing_auth_do_not_mutate(client, ticket):
    task = add(client, ticket)
    path = f"/api/tickets/{ticket}/tasks"
    assert client.get(path).status_code == 401
    assert client.post(path, json={"descripcion": "Actividad"}).status_code == 401
    assert client.post(f"{path}/{task['id']}/complete").status_code == 401
    assert client.post(f"/api/tickets/{ticket}/cancel", headers=auth_headers(5)).status_code == 200
    assert client.post(path, headers=auth_headers(3), json={"descripcion": "Actividad"}).status_code == 422
    assert client.post(f"{path}/{task['id']}/complete", headers=auth_headers(3)).status_code == 422
    assert client.get(path, headers=auth_headers(5)).json() == [task]
