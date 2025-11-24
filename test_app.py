import unittest
import os
from app import app, db, Member, User

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_join_page(self):
        response = self.app.get('/rejoindre.html')
        self.assertEqual(response.status_code, 200)

    def test_join_submission(self):
        response = self.app.post('/rejoindre.html', data=dict(
            nom='Test User',
            email='test@example.com',
            motivation='I want to join!'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Votre demande a \xc3\xa9t\xc3\xa9 envoy\xc3\xa9e avec succ\xc3\xa8s !', response.data)

        with app.app_context():
            member = Member.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(member)
            self.assertEqual(member.nom, 'Test User')

    def test_login_page(self):
        response = self.app.get('/login.html')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
