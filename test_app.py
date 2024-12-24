import unittest
from app import app, db, User

class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Тестовая БД в памяти
        cls.app = app
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()  # Создаем таблицы для тестов

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()  # Удаляем таблицы после тестов

    def test_register_user(self):
        response = self.client.post('/register', json={
            "username": "test_user",
            "password": "password123",
            "subscription_level": "basic",
            "account_status": "active"
        })
        self.assertEqual(response.status_code, 201, f"Expected status code 201, got {response.status_code}")
        self.assertEqual(response.get_json()["message"], "User registered successfully")

    def test_login_user(self):
        self.client.post('/register', json={
            "username": "test_user",
            "password": "password123",
            "subscription_level": "basic",
            "account_status": "active"
        })
        response = self.client.post('/login', json={
            "username": "test_user",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        self.assertIn("access_token", response.get_json())

if __name__ == '__main__':
    unittest.main()