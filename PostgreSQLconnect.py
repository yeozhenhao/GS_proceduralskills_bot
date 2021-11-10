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
        """
            CREATE TABLE IF NOT EXISTS playertaskstodo(
                    playerusername VARCHAR(255) PRIMARY KEY,
                    task1 INTEGER NULL,
                    task2 INTEGER NULL,
                    task3 INTEGER NULL,
                    task4 INTEGER NULL,
                    task5 INTEGER NULL,
                    task6 INTEGER NULL,
                    task7 INTEGER NULL,
                    task8 INTEGER NULL,
                    task9 INTEGER NULL,
                    task10 INTEGER NULL,
                    task11 INTEGER NULL,
                    task12 INTEGER NULL,
                    task13 INTEGER NULL,
                    task14 INTEGER NULL)
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




def loadPlayers_fromSQL(players: dict): ##NOTE: this also loads the chat ids from playerchatids SQL
    command = (
        f"""
            SELECT * FROM
                playertaskstodo
        """
    )
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        cur.execute(command)
        # close communication with the PostgreSQL database server
        print("Selecting rows from playertaskstodo table using cursor.fetchall")
        playerlist_selected = cur.fetchall()
        for row in playerlist_selected:
            playerName = row[0].strip().lower()  ##Note: Player is in 1st column. Angel is in 2nd column, Mortal is in 3rd column.
            taskstodo = list(row)

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
        for k, v in players.items():
            # d = {"playerusername": k, "task1": f"{players[k].taskstodo}"}
            x = players[k].taskstodo
            command2 = (
                f"""
                INSERT INTO playertaskstodo (playerusername,task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14)
                VALUES ({"'" + "','".join(map(str, x)) + "'"})
                ON CONFLICT (playerusername) DO UPDATE 
                SET (playerusername,task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14)
                = ({"'" + "','".join(map(str, x)) + "'"});
                """
            )
            print(x)
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

def saveplayertaskstodo_fromSQL_toCSV(): ##JUST IN CASE FUNCTION
    command = (
        f"""
            SELECT * FROM
                playertaskstodo
        """
    )
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        # create table one by one
        cur.execute(command)
        # close communication with the PostgreSQL database server
        print("Selecting rows from playertaskstodo table using cursor.fetchall")
        playertaskstodo_selected = cur.fetchall()
        # print(playertaskstodo_selected)
        with open(configdualbot.TASKSTODO_CSV, 'w+', newline = '') as f:
            write = csv.writer(f)
            write.writerows(playertaskstodo_selected)
        print("Exported CSV from playertaskstodo table using cursor.fetchall")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)                                    ###NOTE: if you get Index error, open the CSV as notepad, then delete the last empty row. It is a known bug when importing CSVs from CSVs which were exported from SQL. Then it should be able to import flawlessly
    finally:
        if conn is not None:
            conn.close()

def import_playertaskstodo_fromCSV_toSQL(): ##JUST IN CASE FUNCTION
    try:
        conn = psycopg2.connect(host=configdualbot.dbhost, port=5432, database=configdualbot.dbname,
                                user=configdualbot.dbuser, password=configdualbot.dbpassword)
        cur = conn.cursor()
        with open(configdualbot.TASKSTODO_CSV, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                print (f"{row[0]}, {row[1]}")
                cur.execute(
                    f"""
                    INSERT INTO playertaskstodo (playerusername,task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14)
                    VALUES ('{row[0]}','{row[1]}','{row[2]}','{row[3]}','{row[4]}','{row[5]}','{row[6]}','{row[7]}','{row[8]}','{row[9]}','{row[10]}','{row[11]}','{row[12]}','{row[13]}','{row[14]}')
                    ON CONFLICT (playerusername) DO UPDATE SET task1 = '{row[1]}', task2 = '{row[2]}', task3 = '{row[3]}', task4 = '{row[4]}', task5 = '{row[5]}', task6 = '{row[6]}', task7 =
                    '{row[7]}', task8 = '{row[8]}', task9 = '{row[9]}', task10 = '{row[10]}', task11 = '{row[11]}', task12 = '{row[12]}', task13 = '{row[13]}', task14 = '{row[14]}';
                    """
##ALTERNATIVELY, THE CODE BELOW ALSO WORKS
                    # f"""
                    # UPDATE playertaskstodo SET
                    # task1 = '{row[1]}', task2 = '{row[2]}', task3 = '{row[3]}', task4 = '{row[4]}', task5 = '{row[5]}', task6 = '{row[6]}', task7 =
                    # '{row[7]}', task8 = '{row[8]}', task9 = '{row[9]}', task10 = '{row[10]}', task11 = '{row[11]}', task12 = '{row[12]}', task13 = '{row[13]}', task14 = '{row[14]}'
                    # WHERE playerusername = '{row[0]}';
                    # INSERT INTO playertaskstodo (playerusername,task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14)
                    # SELECT '{row[0]}','{row[1]}','{row[2]}','{row[3]}','{row[4]}','{row[5]}','{row[6]}','{row[7]}','{row[8]}','{row[9]}','{row[10]}','{row[11]}','{row[12]}','{row[13]}','{row[14]}'
                    # WHERE NOT EXISTS (SELECT 1 FROM playertaskstodo WHERE playerusername =  '{row[0]}');
                    # """
                ) #### NOTE: ON DUPLICATE KEY UPDATE is SQL command
        print(f"{configdualbot.TASKSTODO_CSV} Dump onto SQL success!")
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        print (f"{configdualbot.TASKSTODO_CSV} is imported successfully into playerchatids SQL database")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    testconnect()
    create_sql_players()
    # import_players_from_csv()
    ### import_playertaskstodo_fromCSV_toSQL() ##only important function here
    # loadPlayers_fromSQL(players)
    ## print(f"players loaded to dualbot!")
    # loadChatID_fromSQL(players)
    ## print(f"player chat_ids loaded to dualbot!")
    # saveplayerschatids_toSQL(players)
    # saveplayerchatids_fromSQL_toJSON()





