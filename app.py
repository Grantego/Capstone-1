import os
import requests

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from secret import API_KEY
from forms import UserAddForm, LoginForm, UserEditForm

# from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Team, Player

API_BASE_URL = 'https://v1.american-football.api-sports.io'
CURR_USER_KEY = "curr_user"
YEAR = 2023

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///sports'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# VIEW ROUTES FOR INFO #
        
@app.route('/')
def show_homepage():
    """Render hompage"""

    teams = Team.query.all()
    return render_template('home.html', teams=teams)
### AUTH ROUTES ###---------------------------------------------------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    """Handles new user sign up"""
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                email=form.email.data,
                pwd=form.password.data,
                image_url=form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()
        except IntegrityError:
            flash('Username/email already taken', 'danger')
            return render_template('users/signup.html', form=form)
        session[CURR_USER_KEY] = user.id
        return redirect('/')

    return render_template('users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """login preexisting user"""
    form = LoginForm()

    if form.validate_on_submit():
         user = User.authenticate(username=form.username.data, pwd=form.password.data)
         if user:
             session[CURR_USER_KEY] = user.id
             flash(f'Welcome back {user.username}!', 'success')
             return redirect('/')
         flash('Invalid username/password!', 'danger')
    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """logout user in session"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    flash('Logout successful!', 'success!')
    return redirect('/')

### USER FAVORTIE ROUTES ###--------------------------------------
        
@app.route('/users/toggle-favorite-team/<int:id>', methods=['POST'])
def toggle_favorite_team(id):
    """if valid user, removes favorite if in team_favorites"""
    if not g.user:
        return 'Unauthorized'
    team = Team.query.get_or_404(id)
    if team in g.user.favorite_teams:
        g.user.favorite_teams.remove(team)
        db.session.commit()
        return 'Favorite removed'
    g.user.favorite_teams.append(team)
    db.session.commit()
    return 'Favorite added'


@app.route('/users/toggle-favorite-player/<int:id>', methods=['POST'])
def toggle_favorite_player(id):
    """if valid user, removes favorite if in team_favorites"""
    if not g.user:
        return 'Unauthorized'
    player = Player.query.get_or_404(id)
    if player in g.user.favorite_players:
        g.user.favorite_players.remove(player)
        db.session.commit()
        return 'Favorite removed'
    g.user.favorite_players.append(player)
    db.session.commit()
    return 'Favorite added'

### USER PROFILE ROUTES ###------------------------------

@app.route('/users/<int:id>')
def users_show(id):
    """show user profile."""
    user = User.query.get_or_404(id)
    return render_template('users/show.html', user=user)


@app.route('/users/<int:id>/players')
def show_favorite_players(id):
    """show users favorite players"""
    user = User.query.get_or_404(id)
    offense = [player for player in user.favorite_players if player.group =='Offense']
    defense = [player for player in user.favorite_players if player.group =='Defense']
    special_teams = [player for player in user.favorite_players if player.group =='Special Teams']
    return render_template('users/players.html', user=user, offense=offense, defense=defense, special_teams=special_teams)


@app.route('/users/profile', methods=['GET', 'POST'])
def edit_profile():
    """shows and processes edit form that updats the user profile if authenticated."""
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")
    user = User.query.get_or_404(g.user.id)
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        auth_user = User.authenticate(user.username, form.password.data)
        if auth_user:
            auth_user.username = form.username.data
            auth_user.email = form.email.data
            auth_user.image_url = form.image_url.data
            try:
                db.session.commit()
            except IntegrityError:
                flash('Username or email already taken!', 'danger')
                return render_template('users/edit.html', form=form, user=user)
            return redirect(f'/users/{auth_user.id}')
        flash('Invaid credentials.', 'danger')
        return render_template('users/edit.html', form=form, user=user)
    return render_template('users/edit.html', form=form, user=user)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Deletes user if logged in."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]   
    db.session.delete(g.user)
    db.session.commit()
    flash("Account deleted successfully", "success")
    return redirect("/")

@app.route('/users')
def list_users():
    """page that lists all players.  can also take a query string to search by the name."""
    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%"))
    
    return render_template('users/all-users.html', users=users)

### TEAM ROUTES ###--------------------------------------

@app.route('/teams/<int:id>')
def show_team_profile(id):
    """show team profile"""
    team = Team.query.get_or_404(id)
    return render_template('teams/show.html', team=team)


@app.route('/teams/<int:id>/offense')
def show_team_offense(id):
    """show team profile"""
    team = Team.query.get_or_404(id)
    all_offense = Player.query.filter(Player.group=='Offense').order_by(Player.name.asc()).all()
    offense = [player for player in all_offense if player.teams[0].id == id]
    return render_template('teams/offense.html', offense=offense, team=team)


@app.route('/teams/<int:id>/defense')
def show_team_defense(id):
    """show team profile"""
    team = Team.query.get_or_404(id)
    all_defense = Player.query.filter(Player.group=='Defense').order_by(Player.name.asc()).all()
    defense = [player for player in all_defense if player.teams[0].id == id]
    return render_template('teams/defense.html', defense=defense, team=team)


@app.route('/teams/<int:id>/special-teams')
def show_team_special_teams(id):
    """show team profile"""
    team = Team.query.get_or_404(id)
    all_special = Player.query.filter(Player.group=='Special Teams').order_by(Player.name.asc()).all()
    special = [player for player in all_special if player.teams[0].id == id]
    return render_template('teams/special-teams.html', special=special, team=team)

### PLAYER ROUTES ###--------------------------------------------------------------------
@app.route('/players')
def list_players():
    """page that lists all players.  can also take a query string to search by the name."""
    search = request.args.get('q')

    if not search:
        players = Player.query.all()
    else:
        players = Player.query.filter(Player.name.like(f"%{search}%"))

        print(players)
    
    return render_template('players/all-players.html', players=players)


@app.route('/players/<int:id>')
def show_player_profile(id):
    """Show player profile with stats"""
    player = Player.query.get_or_404(id)
    headers = {'x-apisports-key': API_KEY}
    params = {'id': player.lookup_id, 'season': YEAR}

    res = requests.get(f'{API_BASE_URL}/players/statistics', headers=headers, params=params)
    res = res.json()
    if len(res['response']) == 0:
        stat_groups = None
    else:
        stat_groups = res['response'][0]['teams'][0]['groups']
    return render_template('players/stats.html', player=player, stat_groups=stat_groups)