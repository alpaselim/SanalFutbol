import os
import sys

import psycopg2 as dbapi2

INIT_STATEMENTS = [
   
    


    
    """
    create table if not exists Manager(
        manager_id serial primary key,
        manager_name varchar not null,
        manager_agent varchar not null 
        
    )
    """,

    """
    create table if not exists Coach (
        coach_id serial primary key,
        coach_name varchar not null,
        coach_lisans_degree varchar not null,
        coach_nation varchar not null
       
    )
    """,

    """
    create table if not exists League(
        League_id serial primary key,
        League_name varchar not null,
        league_nation varchar not null
    )
    """,



    """
    create table if not exists Referee(
        referee_id serial primary key,
        referee_name varchar not null,
        referee_age integer not null,
        referee_cocart varchar not null
    )
    """,


    """
    create table if not exists Team (
        team_id serial PRIMARY KEY,
        team_name  varchar not null unique,
        team_nation varchar not null,
        Cid integer references Coach(coach_id) on delete set null on update cascade,
        Lid integer references League(league_id) on delete set null on update cascade

        
    )
        
   
    """,


    """
    create table if not exists users (
        id serial PRIMARY KEY,
        fullname VARCHAR NOT NULL,
        username VARCHAR NOT NULL,
        password VARCHAR  NOT NULL,
        email VARCHAR NOT NULL,
        Tid integer references Team(team_id) on delete set null on update cascade

       

    )
        
    """, 

    
    
    """
    
    create table if not exists Player (
        player_id serial PRIMARY KEY,
        player_name  varchar not null,
        player_surname  varchar not null,
        preferred_foot varchar not null,
        position varchar not null,
        age integer not null,
        Tid integer references team (team_id) on delete set null on update cascade,
        player_nation varchar not null,
        player_value decimal not null
      
        
 
    )
    
    """,

    
  
     """
        create table if not exists Game(
        game_id serial primary key,
        ref_id integer references Referee(referee_id) on delete set null on update cascade,
        home_team_name varchar not null references team(team_name) on delete set null on update cascade,
        away_team_name varchar not null references team(team_name) on delete set null on update cascade,
        home_team_score integer not null default 0,
        away_team_score integer not null default 0,
        game_week varchar not null
    )
    """,

    
     """
        create table if not exists Rate(
        Uid integer references users(id) on delete set null on update cascade,
        Pid integer references Player(player_id) on delete set null on update cascade,
        point integer not null default 0
        
       
        
    )
    """,


    """
        create table if not exists Manage(
        Mid integer references Manager(manager_id) on delete set null on update cascade,
        Pid integer references Player(player_id) on delete set null on update cascade
        
    )
    """,


    """
        create table if not exists Comment(
        Userid integer references users(id) on delete set null on update cascade,
        Gameid integer references Game(game_id) on delete set null on update cascade,
        content varchar not null,
        primary key (Userid,Gameid)
    )
    
    """

 




]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py")  # , file=sys.stderr)
        sys.exit(1)
    initialize(url)