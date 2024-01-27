from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.
    """
    app.app_context().push()   
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, default="/static/default-pic.png")

    favorite_teams = db.relationship('Team', secondary='favorite_teams', backref='users')

    favorite_players = db.relationship('Player', secondary='favorite_players', backref='users')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def register(cls, username, email, pwd, image_url):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        user = User(username=username, email=email, password=hashed_utf8, image_url=image_url)

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
        
    def is_favorite_team(self, other_team):
        """Has this user favorited `other_team`?"""

        found_team_list = [team for team in self.favorite_teams if team == other_team]
        return len(found_team_list) == 1

    def is_favorite_player(self, other_player):
        """has this user favorited `other_player`?"""

        found_player_list = [player for player in self.favorite_players if player.id == other_player.id]
        return len(found_player_list) == 1

    

class Team(db.Model):
    """Team in the system"""
    __tablename__= 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    city = db.Column(db.Text, nullable=False)

    coach = db.Column(db.Text, nullable=False, unique=True)

    owner = db.Column(db.Text)

    stadium = db.Column(db.Text, nullable=False)
    
    established = db.Column(db.Integer)

    lookup_id = db.Column(db.Integer)

    logo = db.Column(db.Text, default='/static/default-pic.png')

    players = db.relationship('Player', secondary='team_players', backref='teams')


class TeamFavorites(db.Model):
    """Connects user to team"""
    __tablename__= 'favorite_teams'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='cascade'), primary_key=True)

    
class Player(db.Model):
    """Player in the system"""
    __tablename__= 'players'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    age = db.Column(db.Integer)

    height = db.Column(db.Text, default='Unknown')

    weight = db.Column(db.Text, default='Unknown')

    college = db.Column(db.Text, default='Unknown')

    group = db.Column(db.Text, default='Unknown')

    position = db.Column(db.Text, default='Unknown')

    number = db.Column(db.Integer)

    salary = db.Column(db.String, default='Unknown')
    
    seasons = db.Column(db.Integer)

    image_url = db.Column(db.Text, default='/static/default-pic.png')

    lookup_id = db.Column(db.Integer)





class PlayerFavorites(db.Model):
    """connects players with users"""
    __tablename__= 'favorite_players'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)

    player_id = db.Column(db.Integer, db.ForeignKey('players.id', ondelete='cascade'), primary_key=True)


class TeamPlayers(db.Model):

    __tablename__= 'team_players'

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='cascade'), primary_key=True)

    player_id = db.Column(db.Integer, db.ForeignKey('players.id', ondelete='cascade'), primary_key=True)