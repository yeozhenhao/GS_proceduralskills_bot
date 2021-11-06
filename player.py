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


playertasks = {"1": "1. Arterial blood gas",
              "2": "2. Aseptic Blood Culture<b>*</b>",
              "3": "3. Basic processes in theatre (maintain sterility, time out process, surgical gowning)",
              "4": "4. Basic suturing skills",
              "5": "5. Blood transfusion<b>**</b>",
              "6": "6. Dispose of needles and sharps safely after venepuncture, Intravenous (IV) cannulation and other invasive procedures<b>***</b>",
              "7": "7. Hand wash and Scrub",
              "8": "8. Parenteral administration of drugs [including Intravenous (IV)/ Intramuscular (IM)/ Subcutaneous (SC) injections]",
              "9": "9. Removal of surgical drains",
              "10": "10. Urinary catheterization",
              "11": "11. Venepuncture<b>*</b>",
              "12": "12. Bedside arterial doppler<b>*</b>",
              "13": "13. Central line removal [includes Care of Peripherally Inserted Central Catheter (PICC)]",
              "14": "14. Incision and Drainage (abscess)",
              }

tasksinfo = {"*": "<b>*</b> - These procedures can be done in clinic; bedside arterial Doppler - vascular clinic",
                  "**": "<b>**</b> - Blood transfusion can be completed by participating in checking patient identity/blood pack identity with doctor/nurse – not necessarily connecting-up the blood transfusion"}

class Player():
    def __init__(self):
        self.username = None
        self.name = None ## not used
        # self.tasks = {"1", "1. Arterial blood gas",
        #               "2", "2. Aseptic Blood Culture*",
        #               "3", "3. Basic processes in theatre (maintain sterility, time out process, surgical gowning)",
        #               "4", "4. Basic suturing skills",
        #               "5", "5. Blood transfusion**",
        #               "6", "6. Dispose of needles and sharps safely after venepuncture, Intravenous (IV) cannulation and other invasive procedures***",
        #               "7", "7. Hand wash and Scrub",
        #               "8", "8. Parenteral administration of drugs [including Intravenous (IV)/ Intramuscular (IM)/ Subcutaneous (SC) injections]",
        #               "9", "9. Removal of surgical drains",
        #               "10", "10. Urinary catheterization",
        #               "11", "11. Venepuncture*",
        #               "12", "12. Bedside arterial doppler*",
        #               "13", "13. Central line removal [includes Care of Peripherally Inserted Central Catheter (PICC)]",
        #               "14", "14. Incision and Drainage (abscess)",
        #               }
        self.taskstodo = [0, 1, 2, 2, 2, 1, 1, 3, 1, 1, 2, 3, 1, 1, 1]

'''
VERY VERY IMPT: 1st Column in CSV is the Player, 2nd Column is his/her Angel, 3rd Column is his/her Mortal, and the other columns must match the details of the Player in the 1st Column
'''

def loadPlayers(players: dict):
    with open(configdualbot.PLAYERS_FILENAME) as csv_file:
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


# def savemortalUsername(players: dict): ##Important for mortal_command
#     temp = {}
#     for k, v in players.items():
#         temp[k] = v.mortal.username
#
#     with open(configdualbot.MORTAL_USERNAME_JSON, 'w+') as f:
#         json.dump(temp, f)

def saveTasks(players: dict):
    temp = []
    for k, v in players.items():
        d = {"playerusername": k, "tasks": players[k].chat_id}
        temp.append(d)

    with open(configdualbot.TASKS_JSON, 'w+') as f:
        json.dump(temp, f)

def loadTasks(players: dict):
    try:
        with open(configdualbot.TASKS_JSON, 'r') as f:
            temp = json.load(f)
            logger.info(temp)
            for player in temp:
                playerName = player["playerusername"]
                tasks = player["tasks"]
                players[playerName].tasks = tasks
                print (f"player {playerName} with tasks {players[playerName].tasks} has been loaded from local TASKS_JSON")

    except:
        logger.warn('Fail to load chat ids')