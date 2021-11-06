import configdualbot

MESSAGE_SENT = 'Message sent!'
MESSAGE_SENT_TO_GAMEMASTER = 'Message sent to the Game Master! You may now click other buttons in the main menu.'
HELP_TEXT_ANGEL = (
    f'This bot supports forwarding text, emojis, photos, stickers, documents, audio, videos, and animations.'
    f'\n\n'
    f"Type /start if your messages aren't getting sent"
    f'\n\n'
    f'Please click the buttons below to find out more about your {configdualbot.ANGEL_ALIAS}\n\n'
    f'After that, you may click the button below to start messaging your {configdualbot.ANGEL_ALIAS} anonymously!'
)
HELP_TEXT_MORTAL = (
    f'This bot supports forwarding text, emojis, photos, stickers, documents, audio, videos, and animations.'
    f'\n\n'
    f"Type /start if your messages aren't getting sent"
    f'\n\n'
    f'Please click the buttons below to find out more about your {configdualbot.MORTAL_ALIAS}\n\n'
    f'After that, you may click the button below to start messaging your {configdualbot.MORTAL_ALIAS} anonymously!'
)
ERROR_CHAT_ID = f'Sorry an error occurred please type /start again'
# SEND_COMMAND = f'Send a message to my:\n'
NOT_REGISTERED = f'Sorry you are not registered with the game currently'
def STOPPED_BOT(alias):
    return f'Sorry your {alias} has stopped the bot. He/she must restart it for your messages to be sent.\n\nYou may now click the other buttons.'

def getBotNotStartedMessage(alias):
    return f'Sorry your {alias} has not started this bot yet.\n' \
           f'Please try again later.'

def getPlayerMessage(alias):
    return f'From now on, all your messages will be sent to your {alias}. Have fun chatting!\n\n' \
           f'Type /cancel if you want to go back and find out more about your {alias}\n\n'
           # f"Type /start again if your messages somehow aren't getting sent"

def getSupportMessage():
    return f"Facing an issue? Got a suggestion?\n\n"\
           f'Please type a description of your problem or feedback to be sent to the Game Master.\n\n' \
           f"Type /cancel to go back to the main menu."


'''
not used in dualbot
'''
# def getReceivedMessage(alias, text=""):
#     return f"Message from your {alias}:\n\n{text}" if text != "" else f"Message from your {alias}:"

def getSentMessageLog(alias, sender, receiver):
    return f'{sender} sent a message to their {alias} {receiver}'

def getNotRegisteredLog(alias, sender, receiver):
    return f'{sender} {alias} {receiver} has not started the bot'