# tests/__init__.py
from app import create_app, db
import unittest
import os

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    GOOGLE_CLIENT_ID = 'test-client-id'
    GOOGLE_CLIENT_SECRET = 'test-client-secret'

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()