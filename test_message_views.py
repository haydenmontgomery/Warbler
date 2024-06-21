"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import create_app, CURR_USER_KEY
app = create_app('warbler-test', testing=True)

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 9999
        self.testuser.id = self.testuser_id
        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_see_message_form(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)            
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add my message', html)

    def test_see_message(self):
        """Can we see a message when clicked"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Test Text"})
            msg = Message.query.one()

            resp = c.get(f"/messages/{msg.id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test Text', html)

    def test_delete_message(self):
        """Can we delete a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Create the message
            c.post("/messages/new", data={"text": "Test Text"})
            msg = Message.query.one()

            # Delete the message
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            # Test the redirects worked
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Message Deleted', html)

            # Teset the page does not work for the same message id
            resp = c.get(f"/messages/{msg.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn("Woops! Looks like page that doesn't exist!", html)

    def test_like_message(self):
        newuser = User.signup(username="newuser",
                            email="newuser@test.com",
                            password="newuser",
                            image_url=None)
        newuser.id = 1234

        newmsg = Message(id=1234, text="Test Text", user_id=newuser.id)
        db.session.add_all([newuser, newmsg])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/add_like/{newmsg.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('btn-primary', html)


    #####################################
    # No session invalid user tests     #
    #####################################

    def test_add_message_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Test Text"}, follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_invalid_user_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99999

            resp = c.post("/messages/new", data={"text": "Test Text"}, follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_wrong_user_delete_message(self):
        newuser = User.signup(username="newuser",
                                email="newuser@test.com",
                                password="newuser",
                                image_url=None)
        newuser.id = 1234

        newmsg = Message(text="Test Text", user_id=newuser.id)
        db.session.add_all([newuser, newmsg])
        db.session.commit()

        """         print("********************************************")
        print(newmsg.id)
        print(newmsg.user_id)
        print("********************************************") """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{newmsg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            message = Message.query.get(newmsg.id)
            self.assertIsNotNone(message)
        

