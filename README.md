# NFL Player Data
## API: [api-sports.io](https://v1.american-football.api-sports.io/)

## https://nfl-player-data.onrender.com (this may take some time to load)

### This app utilizes the above API to populate a database with information about all players in the NFL, and also provides statistics.  Users can make their own account and save their favorite teams and players.

Resources: Flask, SQLAlchemy, BCrypt, Jinja, WTForms, PostgreSQL.

To run this application locally, please follow these instructions:

1. Clone this repo from Github.
2. Create a virtual environment, and download the requirements.txt.
    ```
    $ python3.12 -m venv venv
    ```
    ```
    $ source venv/bin/activate
    ```
    ```
    $ pip install -r requirements.txt
    ```

3. Register with the API at https://dashboard.api-football.com/register to get an API key
4. Add this API key in a "secret.py" file with the variable name "API_KEY"
    ```
    API_KEY = "(insert api key from step three)"
    ```
    
6. Create a PostgreSQLda database named "sports". (For testing, "sportstest")
    ```
    $ sudo service postgresql start
    ```
    enter in your password for your machine to continue.
   
    ```
    $ psql
    ```
    ```
    \# CREATE DATABASE sports;
    ```
    ```
    \# CREATE DATABASE sportstest;
    ```
   
8. Run the seed.py file when in the project directory.  Due to restrictions of call rates, this file will take 4-5 minutes to populate the database. DO NOT INTERRUPT OR CLOSE THE TERMINAL.
    ```
    $ python3.12 seed.py
    ```
10. Run the application using Flask.
    ```
    $ flask run
    ```

Upon every restart of your computer, you will need to run the below code before running the flask server (step 10).
    ```
    $ sudo service postgresql start
    ```
    
