import configdualbot
import psycopg2
import csv

import player

import collections

import logging
import datetime

import json
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    filename=f'logs/{datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")}.log',
    filemode='w',
    format='PostgreSQL - %(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

players = collections.defaultdict(player.Player)

"""Connect to the PostgreSQL database server """
# conn = psycopg2.connect(host=configdualbot.dbhost, port = 5432, database=configdualbot.dbname, user=configdualbot.dbuser, password=configdualbot.dbpassword)


'''
Use the function below in another 'database.ini' file if you want to save db info
in the .ini file
'''
# from configparser import ConfigParser
# def config(filename='database.ini', section='postgresql'):
#     # create a parser
#     parser = ConfigParser()
#     # read config file
#     parser.read(filename)
#
#     # get section, default to postgresql
#     db = {}
#     if parser.has_section(section):
#         params = parser.items(section)
#         for param in params:
#             db[param[0]] = param[1]
#     else:
#         raise Exception('Section {0} not found in the {1} file'.format(section, filename))
#
#     return db


def testconnect():
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def create_sql_players():
    """ drop tables if exist in the PostgreSQL database"""
    """ create tables in the PostgreSQL database"""
    commands = (
        f"""
            DROP TABLE IF EXISTS
                playerlist,
                playerchatids;
        
        """,
        f"""
        CREATE TABLE playerlist (
            Player VARCHAR(255) PRIMARY KEY,
            Angel VARCHAR(255) NOT NULL,
            Mortal VARCHAR(255) NOT NULL,
            Gender VARCHAR(255) NOT NULL,
            Interests VARCHAR(255) NOT NULL,
            Twotruthsonelie VARCHAR(255) NOT NULL,
            Intro VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE playerchatids (
                playerusername VARCHAR(255) PRIMARY KEY,
                chat_id INTEGER NULL,
                FOREIGN KEY (playerusername)
                REFERENCES playerlist (Player)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        DROP TYPE IF EXISTS stringint;
        CREATE TYPE stringint AS (playerusername text, chat_id int);
        """,
        )
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def import_players_from_csv():
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        with open(configdualbot.PLAYERS_FILENAME, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)  # Skip the header row.
            for row in reader:
                cur.execute(
                    f"""
                    INSERT INTO playerlist VALUES ('{row[0]}','{row[1]}','{row[2]}','{row[3]}','{row[4]}','{row[5]}','{row[6]}')
                    ON CONFLICT DO NOTHING
                    """
                )
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        print (f"PLAYERS_FILENAME imported successfully into SQL database")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def loadPlayers_fromSQL(players: dict): ##NOTE: this also loads the chat ids from playerchatids SQL
    commands = (
        f"""
            SELECT * FROM
                playerlist;

        """,
    )
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        print("Selecting rows from playerlist table using cursor.fetchall")
        playerlist_selected = cur.fetchall()
        for row in playerlist_selected:
            print(row)
            playerName = row[0].strip().lower()  ##Note: Player is in 1st column. Angel is in 2nd column, Mortal is in 3rd column.
            angelName = row[1].strip().lower()
            mortalName = row[2].strip().lower()
            genderPlayer = row[3].strip().lower()
            interests = row[4].strip().lower()
            twotruthsonelie = row[5].strip().lower()
            introduction = row[6].strip().lower()

            players[playerName].username = playerName
            players[playerName].angel = angelName  ###NOTE: DO NOT USE these two lines of code as they DO NOT WORK. When it processes the first row,
            players[playerName].mortal = mortalName  ###the usernames & details of the Angel & Mortal have not been initialised yet.
            players[playerName].gender = genderPlayer
            players[playerName].interests = interests
            players[playerName].twotruthsonelie = twotruthsonelie
            players[playerName].introduction = introduction

        # close communication with the PostgreSQL database server
        temp = players
        for k, v in players.items():
            temp[k].angel = players[v.angel]
            temp[k].mortal = players[v.mortal]
        print(f"players loaded into Telegram dualbot!")
        players = temp
        player.validatePairings(players)
        loadChatID_fromSQL(players)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def loadChatID_fromSQL(players: dict):
    commands = (
        f"""
            SELECT * FROM
                playerchatids;

        """,
    )
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        print("Selecting rows from playerchatids table using cursor.fetchall")
        playerchatids_selected = cur.fetchall()
        for row in playerchatids_selected:
            playerName = row[0].strip().lower()
            chatid = row[1]
            players[playerName].chat_id = chatid
        # close communication with the PostgreSQL database server
        cur.close()
        print(f"player chat_ids loaded to dualbot!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# def saveplayerchatids_toSQL(playerusername, chat_id): ###this function works but it's too slow to manually add one by one
#     commands = (
#         f"""
#             INSERT INTO playerchatids (playerusername, chat_id)
#             VALUES ('{playerusername}', '{chat_id}')
#             ON CONFLICT (playerusername)
#             DO NOTHING
#         """,
#     )
#     try:
#         conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
#                                 user=configdualbot.dbuser, password=configdualbot.dbpassword)
#         cur = conn.cursor()
#         # create table one by one
#         for command in commands:
#             cur.execute(command)
#         conn.commit()
#         count = cur.rowcount
#         print (f"{count} row of chat_id {chat_id} for player {playerusername} is saved!")
#         # close communication with the PostgreSQL database server
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()

def saveplayerschatids_toSQL(players: dict): ##USE THIS INSTEAD OF ABOVE FUNCTION
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        data = []
        for k, v in players.items():
            d = {"playerusername": k, "chat_id": players[k].chat_id}
            data.append(d)
        command1 = (
            f"""
            DROP TABLE IF EXISTS
            playerchatids;
            """,
            f"""
            CREATE TABLE IF NOT EXISTS playerchatids(
                    playerusername VARCHAR(255) PRIMARY KEY,
                    chat_id INTEGER NULL,
                    FOREIGN KEY (playerusername)
                    REFERENCES playerlist (Player)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        for commands in command1:
            cur.execute(commands)
        print("Command 1 success!")
        command2 = (
            f"""
            INSERT INTO playerchatids
            SELECT * FROM jsonb_populate_recordset(null::stringint, '{json.dumps(data)}') AS p
            """
        )
        cur.execute(command2)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        print("All Telegram players chat_id were dumped onto playerchatids SQL successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def saveplayerchatids_fromSQL_toJSON(): ##JUST IN CASE FUNCTION
    commands = (
        f"""
            SELECT * FROM
                playerchatids;

        """,
    )
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        print("Selecting rows from playerchatids table using cursor.fetchall")
        playerchatids_selected = cur.fetchall()

        with open(configdualbot.CHAT_ID_JSON, 'w+') as f:
            json.dump(playerchatids_selected, f)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def import_playerchatids_fromJSON_toSQL(): ##JUST IN CASE FUNCTION
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        with open(configdualbot.CHAT_ID_JSON, 'r') as f:
            data = json.load(f)
        command1 = (
            f"""
            DROP TABLE IF EXISTS
            playerchatids;
            """,
            f"""
            CREATE TABLE IF NOT EXISTS playerchatids(
                    playerusername VARCHAR(255) PRIMARY KEY,
                    chat_id INTEGER NULL,
                    FOREIGN KEY (playerusername)
                    REFERENCES playerlist (Player)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        command2 = (
            f"""
            INSERT INTO playerchatids
            SELECT * FROM json_populate_recordset(null::stringint, '{json.dumps(data)}')
            """
        )
        for commands in command1:
            cur.execute(commands)
        print("Command 1 success!")
        cur.execute(command2)
        print("CHAT_ID_JSON Dump onto SQL success!")
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        print (f"CHAT_ID_JSON is imported successfully into playerchatids SQL database")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    # testconnect()
    create_sql_players()
    import_players_from_csv()
    # import_playerchatids_fromJSON_toSQL()
    # loadPlayers_fromSQL(players)
    ## print(f"players loaded to dualbot!")
    # loadChatID_fromSQL(players)
    ## print(f"player chat_ids loaded to dualbot!")
    # saveplayerschatids_toSQL(players)
    # saveplayerchatids_fromSQL_toJSON()





