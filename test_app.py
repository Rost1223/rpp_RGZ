import pytest
from app import app, db, User, Resource

@pytest.fixture
def client():
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
    client.post('/register', json={
        "username": "test_user",
        "password": "password123",
        "subscription_level": "basic",
        "account_status": "active"
    })
    response = client.post('/login', json={
        "username": "test_user",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()