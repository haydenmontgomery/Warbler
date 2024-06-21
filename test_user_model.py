"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import create_app

app = create_app('warbler-test', testing=True)
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")
        

    def test_follow_isfollowed_model(self):
        """Does basic following work?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )



        db.session.add(u2)
        db.session.commit()
        
        u2.followers.append(u)
        db.session.commit()

        self.assertEqual(u.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u), True)
        

        """Now test for removal"""
        u2.followers.remove(u)
        db.session.commit()

        self.assertEqual(u.is_following(u2), False)
        self.assertEqual(u2.is_followed_by(u), False)

    def test_user_signup_success_model(self):
        u = User.signup(username='testuser', email='test@test.com', password='HASHED_PASSWORD', image_url='/static/images/default-pic.png')
        db.session.commit()
        
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_signup_username_failure_model(self):
        badu = User.signup(None, email='test@test.com', password='HASHED_PASSWORD', image_url='/static/images/default-pic.png')
            
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_user_signup_email_failure_model(self):
        badu = User.signup(username='testuser', email=None, password='HASHED_PASSWORD', image_url='/static/images/default-pic.png')
            
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_signup_password_failure_model(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_user_authenticate(self):
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="pass123", 
            image_url=None
        )
        db.session.add(u)
        db.session.commit()

        auth = User.authenticate(u.username, "pass123")
        self.assertIsNotNone(auth)
        self.assertEqual(u.id, auth.id)
    
    def test_invalid_username_authenticate(self):
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="pass123", 
            image_url=None
        )
        db.session.add(u)
        db.session.commit()
        self.assertFalse(User.authenticate("wrong name", "pass123"))
    
    def test_invalid_password_authenticate(self):
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="pass123", 
            image_url=None
        )
        db.session.add(u)
        db.session.commit()
        self.assertFalse(User.authenticate("testuser", "wrongpass"))