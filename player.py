import config
import csv
import json
import logging
from functools import wraps

import configdualbot

logger = logging.getLogger(__name__)

def restricted(func):
    """Restrict usage of func to allowed users only and replies if necessary"""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.message.chat.id
        if user_id != int(configdualbot.gamemasterchatid):
            print(f"WARNING: Unauthorized access denied for {user_id}.")
            update.message.reply_text('User disallowed.')
            return  # quit function
        return func(update, context, *args, **kwargs)
    return wrapped


class Player():
    def __init__(self):
        self.username = None
        self.name = None ## not used
        self.angel = None
        self.mortal = None
        self.chat_id = None
        self.gender = None
        self.interests = None
        self.twotruthsonelie = None
        self.introduction = None

'''
VERY VERY IMPT: 1st Column in CSV is the Player, 2nd Column is his/her Angel, 3rd Column is his/her Mortal, and the other columns must match the details of the Player in the 1st Column
'''

def loadPlayers(players: dict):
    with open(config.PLAYERS_FILENAME) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                logger.info(f'Column names are {", ".join(row)}')
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                playerName = row[0].strip().lower() ##Note: Player is in 1st column. Angel is in 2nd column, Mortal is in 3rd column.
                angelName = row[1].strip().lower()
                mortalName = row[2].strip().lower()
                genderPlayer = row[3].strip().lower()
                interests = row[4].strip().lower()
                twotruthsonelie = row[5].strip().lower()
                introduction = row[6].strip().lower()

                players[playerName].username = playerName
                players[playerName].angel = angelName            ###NOTE: DO NOT USE these two lines of code as they DO NOT WORK. When it processes the first row,
                players[playerName].mortal = mortalName          ###the usernames & details of the Angel & Mortal have not been initialised yet.
                players[playerName].gender = genderPlayer
                players[playerName].interests = interests
                players[playerName].twotruthsonelie = twotruthsonelie
                players[playerName].introduction = introduction
                line_count += 1
        logger.info(f'Basic information processed for {line_count} lines.')
    '''
    With the basic information processed, we can now match the Player objects together 
    through Angel-Mortal pairings
    '''
    temp = players
    for k, v in players.items():
        temp[k].angel = players[v.angel]
        temp[k].mortal = players[v.mortal]
    players = temp
    validatePairings(players)
    loadChatID(players)


def validatePairings(players: dict):
    logger.info(f'Processing {players.items()}.')
    for _, player in players.items():
        if player.angel.mortal.username != player.username or player.mortal.angel.username != player.username:
            print(f'Error with {player.username} pairings')
            logger.error(f'Error with {player.username} pairings')
            exit(1)

    logger.info(f'Validation complete, no issues with pairings.')


# def savemortalUsername(players: dict): ##Important for mortal_command
#     temp = {}
#     for k, v in players.items():
#         temp[k] = v.mortal.username
#
#     with open(config.MORTAL_USERNAME_JSON, 'w+') as f:
#         json.dump(temp, f)

def saveChatID(players: dict):
    temp = []
    for k, v in players.items():
        d = {"playerusername": k, "chat_id": players[k].chat_id}
        temp.append(d)

    with open(config.CHAT_ID_JSON, 'w+') as f:
        json.dump(temp, f)

def loadChatID(players: dict):
    try:
        with open(config.CHAT_ID_JSON, 'r') as f:
            temp = json.load(f)
            logger.info(temp)
            for player in temp:
                playerName = player["playerusername"]
                chatid = player["chat_id"]
                players[playerName].chat_id = chatid
                print (f"player {playerName} with chat_id {players[playerName].chat_id} has been loaded from local CHAT_ID_JSON")

    except:
        logger.warn('Fail to load chat ids')