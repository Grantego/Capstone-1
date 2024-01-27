"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Player, Team

os.environ['DATABASE_URL'] = "postgresql:///sportstest"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.u1 = User.register("test1", "email1@email.com", "password", None)
        self.uid1 = 1111
        self.u1.id = self.uid1

        self.p1 = Player(name='Player One',
                   age=26,
                   height="6'",
                   weight="200 lbs",
                   college="LSU",
                   group="Offense",
                   position="QB",
                   number=6,
                   salary="$1,000,000",
                   seasons=5,
                   image_url=None,
                   lookup_id=5555)
        self.pid1 = 2222
        self.p1.id = self.pid1

        self.t1 = Team(name="Test Team",
                             city="Kansas City",
                             coach="Coach Test",
                             stadium="Test Stadium")
        self.tid1 = 4321
        self.t1.id = self.tid1

        db.session.add(self.p1)
        db.session.add(self.t1)
        db.session.commit()


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
        self.assertEqual(len(u.favorite_players), 0)
        self.assertEqual(len(u.favorite_teams), 0)

    def test_user_favorite_players(self):
        """Does favoriting a team correctly update model?"""
        self.u1.favorite_players.append(self.p1)
        db.session.commit()

        self.assertEqual(len(self.u1.favorite_players), 1)
        self.assertEqual(len(self.p1.users), 1)

        self.assertEqual(self.u1.favorite_players[0].id, self.p1.id)


    def test_user_favorite_teams(self):
        """Does favoriting a team correctly update model?"""
        self.u1.favorite_teams.append(self.t1)
        db.session.commit()

        self.assertEqual(len(self.u1.favorite_teams), 1)
        self.assertEqual(len(self.t1.users), 1)

        self.assertEqual(self.u1.favorite_teams[0].id, self.t1.id)


    def test_is_favorite_player(self):
        """Does is_favorite_player detect when?"""
        self.u1.favorite_players.append(self.p1)
        db.session.commit()

        self.assertTrue(self.u1.is_favorite_player(self.p1))


    def test_is_favorite_team(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        self.u1.favorite_teams.append(self.t1)
        db.session.commit()

        self.assertTrue(self.u1.is_favorite_team(self.t1))

    def test_register(self):
        """Does sign-up successfully make a new user with a hashed pass?"""
        new_user = User.register('test3', 'test3@test.com', 'password', None)
        uid = 9999
        new_user.id= uid
        db.session.commit()

        new_user = User.query.get(uid)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, 'test3')
        self.assertEqual(new_user.email, 'test3@test.com')
        self.assertNotEqual(new_user.password, 'password')
        self.assertTrue(new_user.password.startswith('$2b$'))

    def test_invalid_username_register(self):
        """tests if a username is already taken returns an error."""
        invalid= User.register('test1', 'test@test.com', 'password', None)
        uid = 9999
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_password_register(self):
        """tests if a password is invalid it returns an error."""
        with self.assertRaises(ValueError) as context:
            User.register('testtest', 'email@email.com', '', None)

        with self.assertRaises(ValueError) as context:
            User.register('testtest', 'email@email.com', None, None)


    def test_invalid_email_register(self):
        """tests if a email is already taken returns an error."""
        invalid = User.register("testtest", None, "password", None)
        uid = 9999
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_authenticate(self):
        """Tests that authenticate properly returns a user on valid login"""
        u = User.authenticate(self.u1.username, 'password')
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    
    def test_invalid_username(self):
        """Tests that authentication returns false on invalid username"""
        self.assertFalse(User.authenticate("invaliduser", "password"))


    def test_invalid_password(self):
        """Tests that authentication returns false on invalid password"""
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))