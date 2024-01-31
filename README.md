# NFL Player Data
## API: [api-sports.io](https://v1.american-football.api-sports.io/)

## https://nfl-player-data.onrender.com

### This app utilizes the above API to populate a database with information about all players in the NFL, and also provides statistics.  Users can make their own account and save their favorite teams and players.

To run this application locally, please follow these instructions.

1. Create a virtual environment, and download the requirements.txt
2. Register with the API at https://dashboard.api-football.com/register to get an API key
3. Add this API key in a "secret.py" file with the variable name "API_KEY"
4. Create a postgresql database named "sports". (For testing, "sportstest")
5. Run the seed.py file.  Due to restrictions of call rates, this file will take a few minutes to populate the database.
6. Run the application using Flask.