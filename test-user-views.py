import os
from unittest import TestCase

from models import db, connect_db, User, Player, Team

os.environ['DATABASE_URL'] = "postgresql:///sportstest"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user pages."""

    def setUp(self):
        """Create test client, add sample data."""
        Team.query.delete()
        Player.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.testplayer = Player(name='Player One',
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
        
        
        self.testplayer_id = 1234
        self.testplayer.id = self.testplayer_id

        self.testteam = Team(name="Test Team",
                             city="Kansas City",
                             coach="Coach Test",
                             stadium="Test Stadium")
        self.testteam_id = 4321
        self.testteam.id = self.testteam_id

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    pwd="testuser",
                                    image_url=None)
        
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id
        self.testuser.favorite_players.append(self.testplayer)
        self.testuser.favorite_teams.append(self.testteam)


        db.session.add(self.testplayer)
        db.session.add(self.testteam)
        db.session.commit()

    def test_show_user_profile(self):
        """Does the user page populate correctly? Does the favorite button only appear when logged in?"""

        with self.client as c:
        
            resp = c.get("/users/1234")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">testuser', str(resp.data))
            self.assertIn('<a href="/teams/4321">Test Team</a>', str(resp.data))
            self.assertNotIn('<i class="fa fa-heart"></i>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('users/1234')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))

    
    def test_show_favorite_players(self):
        """Does the user page for favorite players populate correctly? Does the favorite button only appear when logged in?"""
        with self.client as c:

            resp = c.get('/users/1234/players')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>Player One</p>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get('/users/1234/players')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))

    
    def test_edit_profile(self):
        """Does the edit page populate if the user is logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('/users/profile')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', str(resp.data))

    
    def test_edit_profile_unauthorized(self):
        """Does the edit page return an error if not logged in?"""
        with self.client as c:

            resp = c.get('/users/profile', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))


        
    def test_delete_user(self):
        """Can a user delete their profile successfully if logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post('/users/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Account deleted successfully', str(resp.data))

    
    def test_delete_user_unauthorized(self):
        """Will an error be given to the user if not signed in when deleting user?"""
        with self.client as c:

            resp = c.post('/users/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))



    def test_list_users(self):
        """Does the /users route show all users if no query given?"""
        u = User.register(username="newuser",
            email="testtest@test.com",
            pwd="password",
            image_url=None)
        u.id = 9876
        db.session.add(u)
        db.session.commit()

        with self.client as c:

            resp=c.get('/users')
            self.assertIn("<p>testuser</p>", str(resp.data))
            self.assertIn("<p>newuser</p>", str(resp.data))

    
    def test_search_users(self):
        """Does a search query filter users correctly?"""
        u = User.register(username="newuser",
            email="testtest@test.com",
            pwd="password",
            image_url=None)
        u.id = 9876
        db.session.add(u)
        db.session.commit()

        with self.client as c:

            resp=c.get('/users?q=new')
            self.assertNotIn("<p>testuser</p>", str(resp.data))
            self.assertIn("<p>newuser</p>", str(resp.data))       
    
