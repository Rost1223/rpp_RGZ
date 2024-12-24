import pytest
from app import app, db, User, Resource

@pytest.fixture
def client():
    # Настройка тестового клиента и базы данных
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Тестовая БД в памяти
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Создаем таблицы для тестов
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Удаляем таблицы после тестов

def test_register_user(client):
    response = client.post('/register', json={
        "username": "test_user",
        "password": "password123",
        "subscription_level": "basic",
        "account_status": "active"
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

def test_login_user(client):
    # Сначала регистрируем пользователя
    client.post('/register', json={
        "username": "test_user",
        "password": "password123",
        "subscription_level": "basic",
        "account_status": "active"
    })
    # Затем пытаемся войти
    response = client.post('/login', json={
        "username": "test_user",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_add_resource(client):
    # Сначала регистрируем пользователя и получаем токен
    client.post('/register', json={
        "username": "test_user",
        "password": "password123",
        "subscription_level": "basic",
        "account_status": "active"
    })
    login_response = client.post('/login', json={
        "username": "test_user",
        "password": "password123"
    })
    token = login_response.get_json()["access_token"]

    # Добавляем ресурс
    response = client.post('/resources', json={
        "name": "Resource 1",
        "access_level": "basic",
        "available_hours": "09:00-18:00"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.get_json()["message"] == "Resource added successfully"

def test_get_resources(client):
    # Сначала регистрируем пользователя и получаем токен
    client.post('/register', json={
        "username": "test_user",
        "password": "password123",
        "subscription_level": "basic",
        "account_status": "active"
    })
    login_response = client.post('/login', json={
        "username": "test_user",
        "password": "password123"
    })
    token = login_response.get_json()["access_token"]

    # Добавляем ресурс
    client.post('/resources', json={
        "name": "Resource 1",
        "access_level": "basic",
        "available_hours": "09:00-18:00"
    }, headers={"Authorization": f"Bearer {token}"})

    # Получаем список ресурсов
    response = client.get('/resources', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    resources = response.get_json()["resources"]
    assert len(resources) == 1
    assert resources[0]["name"] == "Resource 1"