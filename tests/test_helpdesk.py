import pytest
from fastapi.testclient import TestClient
from app.webs.main import create_app
from app.models import User
from app.core.security import hash_password

PASSWORD = 'TestPassword2026!'

@pytest.fixture
def setup():
    app = create_app('sqlite://')
    with app.state.session_factory() as db:
        for role in ['administrator','technician','supervisor','requester','other']:
            db.add(User(email=role+'@example.com',name=role,role='requester' if role=='other' else role,password_hash=hash_password(PASSWORD)))
        db.commit()
    with TestClient(app) as client:
        yield client, app
    app.state.session_factory.kw['bind'].dispose()

def login(client, role):
    response=client.post('/api/auth/login',json={'email':role+'@example.com','password':PASSWORD})
    assert response.status_code==200
    return {'Authorization':'Bearer '+response.json()['access_token']}

def ticket(client, headers, **kwargs):
    return client.post('/api/tickets',headers=headers,json={'title':'Prueba de conexión','description':'No puedo conectar mi equipo a internet.','category':'Network','priority':'High',**kwargs})

def test_auth_and_static(setup):
    client,_=setup
    assert client.get('/').status_code==200
    assert client.get('/static/app.js').status_code==200
    assert client.get('/api/health').json()=={'status':'ok'}
    assert client.get('/api/tickets').status_code==401
    assert client.get('/api/users/me',headers={'Authorization':'Bearer invalid'}).status_code==401
    assert client.post('/api/auth/login',json={'email':'requester@example.com','password':'wrong'}).status_code==401
    assert client.get('/api/users/me',headers=login(client,'administrator')).json()['role']=='administrator'

def test_requester_isolation_and_roles(setup):
    c,_=setup; owner=login(c,'requester'); other=login(c,'other')
    item=ticket(c,owner).json(); id=item['id']
    assert c.get('/api/tickets',headers=other).json()['items']==[]
    for suffix in ['', '/history']:
        assert c.get(f'/api/tickets/{id}'+suffix,headers=other).status_code==403
    assert c.post(f'/api/tickets/{id}/comments',headers=other,json={'body':'Un comentario'}).status_code==403
    assert c.post(f'/api/tickets/{id}/cancel',headers=other).status_code==403
    assert c.patch(f'/api/tickets/{id}/status',headers=owner,json={'status':'Resolved'}).status_code==403
    assert c.get('/api/users',headers=owner).status_code==403
    assert c.get('/api/assignees',headers=owner).status_code==403

def test_ticket_lifecycle_history_and_dashboard(setup):
    c,_=setup; requester=login(c,'requester'); tech=login(c,'technician'); admin=login(c,'administrator')
    response=ticket(c,requester); assert response.status_code==201
    id=response.json()['id']
    assignee=c.get('/api/assignees',headers=tech).json()[0]
    response=c.patch(f'/api/tickets/{id}/assign',headers=tech,json={'assignee_id':assignee['id']})
    assert response.json()['assignee']==assignee['name']
    assert c.post(f'/api/tickets/{id}/close',headers=tech).status_code==409
    assert c.patch(f'/api/tickets/{id}/status',headers=tech,json={'status':'Closed'}).status_code==409
    assert c.patch(f'/api/tickets/{id}/status',headers=tech,json={'status':'In Progress'}).status_code==200
    assert c.post(f'/api/tickets/{id}/comments',headers=requester,json={'body':'Ya reinicié el equipo.'}).status_code==201
    assert c.patch(f'/api/tickets/{id}/status',headers=tech,json={'status':'Resolved'}).status_code==200
    dashboard=c.get('/api/dashboard',headers=admin).json()
    assert dashboard['open']==0 and dashboard['status']['Resolved']==1
    assert c.post(f'/api/tickets/{id}/close',headers=tech).status_code==200
    assert c.post(f'/api/tickets/{id}/cancel',headers=requester).status_code==409
    detail=c.get(f'/api/tickets/{id}',headers=requester).json()
    assert len(detail['comments'])==1
    assert len(detail['history'])==6
    assert detail['overdue'] is False

@pytest.mark.parametrize('change',[{'title':'  '},{'description':'short'},{'category':'unknown'},{'priority':'urgent'}])
def test_validation(setup,change):
    c,_=setup
    assert ticket(c,login(c,'requester'),**change).status_code==422

def test_articles_and_users(setup):
    c,_=setup; admin=login(c,'administrator'); requester=login(c,'requester'); tech=login(c,'technician')
    body={'title':'Una guía útil','body':'Instrucciones para resolver problemas.','category':'General'}
    assert c.post('/api/knowledge-base',headers=requester,json=body).status_code==403
    response=c.post('/api/knowledge-base',headers=tech,json=body); assert response.status_code==201
    id=response.json()['id']
    assert len(c.get('/api/knowledge-base?q=guía').json())==1
    assert c.patch(f'/api/knowledge-base/{id}',headers=tech,json={**body,'title':'Guía actualizada'}).status_code==200
    assert c.delete(f'/api/knowledge-base/{id}',headers=tech).status_code==403
    assert c.delete(f'/api/knowledge-base/{id}',headers=admin).status_code==204
    assert c.get(f'/api/knowledge-base/{id}').status_code==404
    data={'email':'new@example.com','name':'Nuevo usuario','password':PASSWORD,'role':'requester'}
    assert c.post('/api/users',headers=tech,json=data).status_code==403
    assert c.post('/api/users',headers=admin,json=data).status_code==201
    assert c.post('/api/users',headers=admin,json=data).status_code==409
    assert all('password_hash' not in u for u in c.get('/api/users',headers=admin).json())

def test_persistence(tmp_path):
    url='sqlite:///'+str(tmp_path/'persist.db')
    first=create_app(url)
    with first.state.session_factory() as db:
        db.add(User(email='persist@example.com',name='Persistencia',role='administrator',password_hash=hash_password(PASSWORD)))
        db.commit()
    first.state.session_factory.kw['bind'].dispose()
    second=create_app(url)
    with TestClient(second) as client:
        assert client.post('/api/auth/login',json={'email':'persist@example.com','password':PASSWORD}).status_code==200
    second.state.session_factory.kw['bind'].dispose()
