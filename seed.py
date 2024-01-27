import requests
import time

from app import db, API_BASE_URL, API_KEY
from models import Team, Player



YEAR = 2023

db.drop_all()
db.create_all()

headers = {'x-apisports-key': API_KEY}
params = {'league': 1, 'season': YEAR}

res = requests.get(f'{API_BASE_URL}/teams', headers=headers, params=params)
res = res.json()

teams = res['response']

for team in teams:

    if team['city'] is None:
        continue
    t = Team(name=team['name'],
             city=team['city'],
             coach=team['coach'],
             owner=team['owner'],
             stadium=team['stadium'],
             established=team['established'],
             logo=team['logo'], 
             lookup_id=team['id'])
    db.session.add(t)
    db.session.commit()
    params = {'team': team['id'], 'season': YEAR}
    res2 = requests.get(f'{API_BASE_URL}/players', headers=headers, params=params)
    res2 = res2.json()
    players = res2['response']
    for player in players:
        p = Player(name=player['name'],
                   age=player['age'],
                   height=player['height'],
                   weight=player['weight'],
                   college=player['college'],
                   group=player['group'],
                   position=player['position'],
                   number=player['number'],
                   salary=player['salary'],
                   seasons=player['experience'],
                   image_url=player['image'],
                   lookup_id=player['id'])
        
        t.players.append(p)
        
        db.session.add(p)
        db.session.commit()
    time.sleep(8)