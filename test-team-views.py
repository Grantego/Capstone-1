import os
from unittest import TestCase

from models import db, connect_db, User, Player, Team

os.environ['DATABASE_URL'] = "postgresql:///sportstest"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class TeamViewTestCase(TestCase):
    """Test views for team pages."""

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
        self.testteam.players.append(self.testplayer)

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    pwd="testuser",
                                    image_url=None)
        
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id


        db.session.add(self.testplayer)
        db.session.add(self.testteam)
        db.session.commit()

    def test_show_team_profile(self):
        """does the team page populate correctly? Does the favorite button only appear when logged in?"""
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
        self.testteam.players.append(p)
        db.session.commit()        
        with self.client as c:
        
            resp = c.get("/teams/4321")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">Test Team', str(resp.data))
            self.assertIn('<p>Player One</p>', str(resp.data))
            self.assertIn('<p>Player Two</p>', str(resp.data))
            self.assertNotIn('<i class="fa fa-heart"></i>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('teams/4321')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))

    def test_show_team_offense(self):
        """Does the offense page only display offense players? (also tests favorite heart)"""
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
        self.testteam.players.append(p)
        db.session.commit()        
        with self.client as c:
        
            resp = c.get("/teams/4321/offense")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">Test Team', str(resp.data))
            self.assertIn('<p>Player One</p>', str(resp.data))
            self.assertNotIn('<p>Player Two</p>', str(resp.data))
            self.assertNotIn('<i class="fa fa-heart"></i>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('teams/4321/offense')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))       


    def test_show_team_defense(self):
        """Does the defense page only display defense players? (also tests favorite heart)"""
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
        self.testteam.players.append(p)
        db.session.commit()        
        with self.client as c:
        
            resp = c.get("/teams/4321/defense")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">Test Team', str(resp.data))
            self.assertIn('<p>Player Two</p>', str(resp.data))
            self.assertNotIn('<p>Player One</p>', str(resp.data))
            self.assertNotIn('<i class="fa fa-heart"></i>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('teams/4321/defense')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))  


    def test_show_team_special_teams(self):
        """Does the special teams page only display special teams players? (also tests favorite heart)"""
        p = Player(name='Player Two',
                   age=27,
                   height="5'",
                   weight="200 lbs",
                   college="LSU",
                   group="Special Teams",
                   position="RB",
                   number=10,
                   salary="$1,000,000",
                   seasons=5,
                   image_url=None,
                   lookup_id=6666)
        p.id = 9876
        db.session.add(p)
        self.testteam.players.append(p)
        db.session.commit()        
        with self.client as c:
        
            resp = c.get("/teams/4321/special-teams")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">Test Team', str(resp.data))
            self.assertIn('<p>Player Two</p>', str(resp.data))
            self.assertNotIn('<p>Player One</p>', str(resp.data))
            self.assertNotIn('<i class="fa fa-heart"></i>', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('teams/4321/special-teams')
            self.assertIn('<i class="fa fa-heart"></i>', str(resp.data))       

