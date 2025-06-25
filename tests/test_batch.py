# tests/test_batch.py
from tests import BaseTestCase
from app.models.batch import EmailBatch, BatchApplication
from app.models.learnership import Learnership

class TestBatch(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create test user and learnership
        self.user = User(email='test@example.com', name='Test User', google_id='123')
        self.learnership = Learnership(
            name='Test Learnership',
            company='Test Company',
            email='company@test.com'
        )
        db.session.add_all([self.user, self.learnership])
        db.session.commit()

    def test_batch_creation(self):
        batch = EmailBatch(user_id=self.user.id)
        db.session.add(batch)
        db.session.commit()

        application = BatchApplication(
            batch_id=batch.id,
            learnership_id=self.learnership.id
        )
        db.session.add(application)
        db.session.commit()

        self.assertEqual(batch.applications[0].learnership.name, 'Test Learnership')