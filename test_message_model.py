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

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u1_id = 11111
        u1.id = u1_id

        u2 = User.signup("test2", "email2@email.com", "password", None)
        u2_id = 22222
        u2.id = u2_id

        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)

        self.u1 = u1
        self.uid1 = u1_id

        self.u2 = u2
        self.uid2 = u2_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        msg = Message(text="Test Text")
        self.u1.messages.append(msg)

        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(msg.user_id, self.u1.id)
        

    def test_likes_message_model(self):
        """Does basic liking work?"""

        msg = Message(text="Test Text")
        self.u1.messages.append(msg)
        db.session.commit()

        self.u2.likes.append(msg)
        db.session.commit()
        
        self.assertEqual(len(self.u2.likes), 1)
        self.assertEqual(self.u2.likes[0].user_id, self.u1.id)
        

        """Now test for not liking"""
        self.u2.likes.remove(msg)
        db.session.commit()

        self.assertEqual(len(self.u2.likes), 0)

    def test_message_has_text(self):
        msg = Message(text=None)
        self.u1.messages.append(msg)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_message_id_autoincrements(self):
        msg1 = Message(text="Test Text")
        self.u1.messages.append(msg1)
        db.session.commit()

        msg2 = Message(text="Test Text")
        self.u2.messages.append(msg2)
        db.session.commit()

        self.assertGreater(msg2.id, msg1.id)