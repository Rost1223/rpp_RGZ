import unittest
from app import app, db
from flask import json

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
            # Регистрация пользователя перед тестами
            self.app.post('/register', json={
                "username": "testuser",
                "password": "testpassword",
                "subscription_level": "basic",
                "account_status": "active"
            })
            # Добавление ресурса перед тестами
            access_token = self.get_access_token()
            self.app.post('/resources', json={
                "name": "Resource 1",
                "access_level": "basic",
                "available_hours": "09:00-18:00"
            }, headers={"Authorization": f"Bearer {access_token}"})

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.app.post('/register', json={
            "username": "testuser2",
            "password": "testpassword2",
            "subscription_level": "basic",
            "account_status": "active"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["message"], "User registered successfully")

    def test_login(self):
        response = self.app.post('/login', json={
            "username": "testuser",
            "password": "testpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

    def test_add_resource(self):
        access_token = self.get_access_token()
        response = self.app.post('/resources', json={
            "name": "Resource 2",
            "access_level": "basic",
            "available_hours": "09:00-18:00"
        }, headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["message"], "Resource added successfully")

    def test_get_resources(self):
        access_token = self.get_access_token()
        response = self.app.get('/resources', headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 200)
        resources = response.get_json()["resources"]
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["name"], "Resource 1")

    def get_access_token(self):
        response = self.app.post('/login', json={
            "username": "testuser",
            "password": "testpassword"
        })
        return response.get_json()["access_token"]

if __name__ == '__main__':
    unittest.main()
