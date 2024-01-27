import os
from unittest import TestCase

from models import db, connect_db, User, Player, Team

os.environ['DATABASE_URL'] = "postgresql:///sportstest"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class PlayerViewTestCase(TestCase):
    """Test views for player pages."""

    def setUp(self):
        """Create test client, add sample data."""

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

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    pwd="testuser",
                                    image_url=None)
        
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id


        db.session.add(self.testplayer)
        db.session.commit()

    def test_show_player_profile(self):
        """Does the player page populate correctly? Does the favorite button only appear when logged in?"""
        
        with self.client as c:
        
            resp = c.get("/players/1234")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">Player One', str(resp.data))
            self.assertIn('<p>Weight: 200 lbs', str(resp.data))
            self.assertNotIn('<i class="fa fa-heart"></i>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('players/1234')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))


    def test_list_players(self):
        """Does the /players route show all players if no query given?"""
        p = Player(name='Player Two',
                   age=27,
                   height="5'",
                   weight="200 lbs",
                   college="LSU",
                   group="Defense",
                   position="RB",
                   number=10,
                   salary="$1,000,000",
                   seasons=5,
                   image_url=None,
                   lookup_id=6666)
        p.id = 9876
        db.session.add(p)
        db.session.commit()

        with self.client as c:

            resp=c.get('/players')
            self.assertIn("<p>Player One</p>", str(resp.data))
            self.assertIn("<p>Player Two</p>", str(resp.data))

    
    def test_search_players(self):
        """Does a search query filter players correctly?"""
        p = Player(name='Player Two',
                   age=27,
                   height="5'",
                   weight="200 lbs",
                   college="LSU",
                   group="Defense",
                   position="RB",
                   number=10,
                   salary="$1,000,000",
                   seasons=5,
                   image_url=None,
                   lookup_id=6666)
        p.id = 9876
        db.session.add(p)
        db.session.commit()

        with self.client as c:

            resp=c.get('/players?q=Two')
            self.assertNotIn("<p>Player One</p>", str(resp.data))
            self.assertIn("<p>Player Two</p>", str(resp.data))       