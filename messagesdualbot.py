import configdualbot
import player
from player import playertasks
from player import tasksinfo

gettasksinfo = f'{tasksinfo["*"]}\n\n' \
               f'{tasksinfo["**"]}\n\n'

MESSAGE_SENT = 'Message sent!'
MESSAGE_SENT_TO_GAMEMASTER = 'Message sent to the Game Master! You may now click other buttons in the main menu.'
HELP_TEXT_ANGEL = (
    f'This bot helps to keep track of the procedural tasks in GS.\n')

START_AGAIN = f'Please /start or type anything to bring up the menu again.'

getaddTasksMessage = f"Type the task number & the number of times done, with both separated by a space\n\n"\
           f"Type /cancel to go back to the main menu."

getcompleteTasksMessage= f"Type the task number & the number of times you have completed, with both separated by a space\n\n"\
           f"Type /cancel to go back to the main menu."

typeCanceltogoback = f"Or you may type /cancel to go back to the main menu."


def YOUR_CURRENT_TASKS (playerName, players: dict):
    return f'Your current tasks:'\
    f'\n{playertasks["1"]} <b>x{players[playerName].taskstodo[1]}</b>' \
    f'\n{playertasks["2"]} <b>x{players[playerName].taskstodo[2]}</b>' \
    f'\n{playertasks["3"]} <b>x{players[playerName].taskstodo[3]}</b>' \
    f'\n{playertasks["4"]} <b>x{players[playerName].taskstodo[4]}</b>' \
    f'\n{playertasks["5"]} <b>x{players[playerName].taskstodo[5]}</b>' \
    f'\n{playertasks["6"]} <b>x{players[playerName].taskstodo[6]}</b>' \
    f'\n{playertasks["7"]} <b>x{players[playerName].taskstodo[7]}</b>' \
    f'\n{playertasks["8"]} <b>x{players[playerName].taskstodo[8]}</b>' \
    f'\n{playertasks["9"]} <b>x{players[playerName].taskstodo[9]}</b>' \
    f'\n{playertasks["10"]} <b>x{players[playerName].taskstodo[10]}</b>' \
    f'\n{playertasks["11"]} <b>x{players[playerName].taskstodo[11]}</b>' \
    f'\n{playertasks["12"]} <b>x{players[playerName].taskstodo[12]}</b>' \
    f'\n{playertasks["13"]} <b>x{players[playerName].taskstodo[13]}</b>' \
    f'\n{playertasks["14"]} <b>x{players[playerName].taskstodo[14]}</b>'

ERROR_CHAT_ID = f'Sorry an error occurred please type /start again'



def getSupportMessage():
    return f"Facing an issue? Got a suggestion?\n\n"\
           f'Please type a description of your problem or feedback to be sent to the Game Master.\n\n' \
           f"Type /cancel to go back to the main menu."
