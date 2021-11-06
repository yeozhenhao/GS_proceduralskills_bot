import configdualbot
import psycopg2
import csv

import player

import collections

import logging

import datetime
# import logging
# logging.basicConfig(
#     filename=f'logs/{datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")}.log',
#     filemode='w',
#     format='PostgreSQL - %(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )

import json
from psycopg2.extras import RealDictCursor



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
                playertaskstodo;
        """,
        f"""
        CREATE TABLE IF NOT EXISTS playertaskstodo(
                playerusername VARCHAR(255) PRIMARY KEY,
                taskstodo VARCHAR(255)
        )
        """
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


# def import_players_from_csv():
#     try:
#         conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
#                                 user=configdualbot.dbuser, password=configdualbot.dbpassword)
#         cur = conn.cursor()
#         # create table one by one
#         with open(configdualbot.PLAYERS_FILENAME, 'r') as f:
#             reader = csv.reader(f, delimiter=',')
#             next(reader)  # Skip the header row.
#             for row in reader:
#                 cur.execute(
#                     f"""
#                     INSERT INTO playerlist VALUES ('{row[0]}','{row[1]}','{row[2]}','{row[3]}','{row[4]}','{row[5]}','{row[6]}')
#                     ON CONFLICT DO NOTHING
#                     """
#                 )
#         # close communication with the PostgreSQL database server
#         cur.close()
#         # commit the changes
#         conn.commit()
#         print (f"PLAYERS_FILENAME imported successfully into SQL database")
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()


def loadPlayers_fromSQL(players: dict): ##NOTE: this also loads the chat ids from playerchatids SQL
    commands = (
        f"""
            SELECT * FROM
                playertaskstodo;
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
        print("Selecting rows from playertaskstodo table using cursor.fetchall")
        playerlist_selected = cur.fetchall()
        for row in playerlist_selected:
            print(row)
            playerName = row[0].strip().lower()  ##Note: Player is in 1st column. Angel is in 2nd column, Mortal is in 3rd column.
            taskstodo = row[1]

            players[playerName].username = playerName
            players[playerName].taskstodo = taskstodo

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()




def saveplayertaskstodo_toSQL(players: dict): ##USE THIS INSTEAD OF ABOVE FUNCTION
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        data = []
        for k, v in players.items():
            d = {"playerusername": k, "taskstodo": f"{str(players[k].taskstodo)}"}
            data.append(d)
        command1 = (
            f"""
            DROP TABLE IF EXISTS
            playertaskstodo;
            """,
            f"""
            CREATE TABLE IF NOT EXISTS playertaskstodo(
                    playerusername VARCHAR(255) PRIMARY KEY,
                    taskstodo VARCHAR(255)
            )
            """
        )
        for commands in command1:
            cur.execute(commands)
        print("Command 1 success!")
        command2 = (
            f"""
            INSERT INTO playertaskstodo
            SELECT * FROM jsonb_populate_recordset(null::stringint, '{json.dumps(data)}') AS p
            """
        )
        cur.execute(command2)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        print("All Telegram players taskstodo were dumped onto playertaskstodo SQL successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def saveplayertaskstodo_fromSQL_toJSON(): ##JUST IN CASE FUNCTION
    commands = (
        f"""
            SELECT * FROM
                playertaskstodo;
        """
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
        playertaskstodo_selected = cur.fetchall()

        with open(configdualbot.TASKSTODO_JSON, 'w+') as f:
            json.dump(playertaskstodo_selected, f)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def import_playertaskstodo_fromJSON_toSQL(): ##JUST IN CASE FUNCTION
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        with open(configdualbot.TASKSTODO_JSON, 'r') as f:
            data = json.load(f)
        command1 = (
            f"""
            DROP TABLE IF EXISTS
            playertaskstodo;
            """,
            f"""
            CREATE TABLE IF NOT EXISTS playertaskstodo(
                    playerusername VARCHAR(255) PRIMARY KEY,
                    taskstodo VARCHAR(255),
            )
            """
        )
        command2 = (
            f"""
            INSERT INTO playertaskstodo
            SELECT * FROM jsonb_populate_recordset(null::stringint, '{json.dumps(data)}') AS p
            """
        )
        for commands in command1:
            cur.execute(commands)
        print("Command 1 success!")
        cur.execute(command2)
        print(f"{configdualbot.TASKSTODO_JSON} Dump onto SQL success!")
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        print (f"{configdualbot.TASKSTODO_JSON} is imported successfully into playerchatids SQL database")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    testconnect()
    create_sql_players()
    # import_players_from_csv()
    ### import_playertaskstodo_fromJSON_toSQL() ##only important function here
    # loadPlayers_fromSQL(players)
    ## print(f"players loaded to dualbot!")
    # loadChatID_fromSQL(players)
    ## print(f"player chat_ids loaded to dualbot!")
    # saveplayerschatids_toSQL(players)
    # saveplayerchatids_fromSQL_toJSON()





