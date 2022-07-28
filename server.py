import os
from db_init import initialize
import re 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from queries import *

from psycopg2   import extensions

extensions.register_type(extensions.UNICODE)

extensions.register_type(extensions.UNICODEARRAY)

app = Flask(__name__)



os.environ['DATABASE_URL'] = "dbname='postgres' user='postgres' host='localhost' password='1234'"
initialize(os.environ.get('DATABASE_URL'))



app.secret_key = 'cairocoders-ednalan'
 
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "1234"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
    
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')
   
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/players', methods=['GET', 'POST'])
def player_page():
    if request.method == 'GET':
        player = select("player_id,player_name,player_surname,player_nation,position,point,player_value","player join rate on player_id = rate.Pid",asDict=True)
        return render_template('players.html', player = player )
    elif request.method == 'POST':
        if "like" in request.form:
            update ("rate","point = point + 1", "Pid={}".format(request.form.get('like'))) 
        elif "dislike" in request.form:
            update ("rate","point = point - 1", "Pid={}".format(request.form.get('dislike'))) 
        return redirect(url_for("player_page"))


    

@app.route('/leagues')
def league_page():
    leagues = select("league_id,league_name,league_nation","league",asDict=True)
    return render_template('leagues.html', leagues = leagues )

@app.route('/teams')
def team_page():
    teams = select("team_id,team_name,team_nation,Cid,Lid","team",asDict=True)
    return render_template('teams.html', teams = teams )

@app.route('/referee')
def referee_page():
    referees = select("referee_id,referee_name,referee_age,referee_cocart","Referee",asDict=True)
    return render_template('referees.html', referees = referees )


@app.route('/manager')
def manager_page():
    managers = select("manager_id,manager_name,manager_agent","manager",asDict=True)
    return render_template('managers.html', managers = managers )


@app.route('/coach')
def coach_page():
    coaches = select("coach_id,coach_name,coach_lisans_degree,coach_nation,team_name","coach join team on coach_id = team.Cid",asDict=True)
    return render_template('coaches.html', coaches = coaches )


@app.route('/game')
def game_page():
    games = select("game_id,ref_id,home_team_name,away_team_name,home_team_score,away_team_score,game_week","game",asDict=True)
    return render_template('games.html', games = games )






@app.route('/teams/<team_id>')
def team_detail_page(team_id):
    team = select("team_name","team","team_id={}".format(team_id),asDict=True)
    players = select("player.player_name,player.player_surname,player.age,player.position,player.player_nation,player.player_value","player join team on player.Tid = team.team_id","player.Tid={}".format(team_id),asDict=True)
    return render_template("team_detail_page.html",team=team,players = players)

@app.route('/leagues/<league_id>')
def league_detail_page(league_id):
    league = select("league_name","league","league_id={}".format(league_id),asDict=True)
    teams = select("team.team_name","team join league on team.Lid = league.League_id","team.Lid={}".format(league_id),asDict=True)
    return render_template("league_detail_page.html",league=league,teams = teams)

@app.route('/manager/<manager_id>')
def manager_detail_page(manager_id):
    manager = select("manager_name","manager","manager_id={}".format(manager_id),asDict=True)
    players = select("player.player_name,player.player_surname,player.age,player.player_value","player join manage on player.player_id = manage.Pid","manage.Mid={}".format(manager_id),asDict=True)
    return render_template("manager_detail_page.html",manager=manager,players = players)


@app.route('/referee/<referee_id>')
def referee_detail_page(referee_id):
    referee = select("referee_name","referee","referee_id={}".format(referee_id),asDict=True)
    games = select("game.home_team_name,game.away_team_name","game join referee on game.ref_id = referee.referee_id","referee.referee_id={}".format(referee_id),asDict=True)
    return render_template("referee_detail_page.html",referee=referee, games = games)






if __name__ == "__main__":
    app.run(debug=True)
    


