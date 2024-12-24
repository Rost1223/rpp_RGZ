import pytest

@pytest.fixture
def client():
    from app import app  # Импортируйте ваше Flask приложение
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_user(client):
    response = client.post('/register', json={
        "username": "test_user",
        "password": "password123",
        "subscription_level": "basic",
        "account_status": "active"
    })
    assert response.status_code == 201  # Ожидаем статус 201 (создано)

def test_login_user(client):
    # Сначала регистрируем пользователя
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
    assert response.status_code == 200  # Ожидаем статус 200 (успех)
    assert "access_token" in response.get_json()  # Проверяем наличие токена

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
        "available_hours": "09:00-18:00",
        "description": "Описание ресурса"  # Добавьте недостающее поле
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 201  # Ожидаем статус 201 (создано)

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
        "available_hours": "09:00-18:00",
        "description": "Описание ресурса"  # Добавьте недостающее поле
    }, headers={"Authorization": f"Bearer {token}"})

    # Получаем список ресурсов
    response = client.get('/resources', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # Ожидаем статус 200 (успех)
    assert isinstance(response.get_json(), list)  # Проверяем, что возвращается список