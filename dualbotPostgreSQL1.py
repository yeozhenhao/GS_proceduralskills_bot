import logging

import player
import messagesdualbot
import datetime
import collections
import PostgreSQLconnect

import configdualbot
import telegram
from telegram import ParseMode

import os ##for heroku setup
PORT = int(os.environ.get('PORT', '8443')) ##for heroku setup. See https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler

GAMEMASTERSUPPORT, CHOOSING, ADDTASKS, REMOVETASKS = range(4)

# Enable logging
logging.basicConfig(
    filename=f'logs/{datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")}.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ANGEL_BOT_TOKEN = configdualbot.ANGEL_BOT_TOKEN

herokuappname = configdualbot.herokuappname

players = collections.defaultdict(player.Player)
# PostgreSQLconnect.loadPlayers_fromSQL(players)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def start_Angelbot(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    playerName = update.message.chat.username.lower()
    if players[playerName].username is None:
        players[playerName].username = playerName
        update.message.reply_text(f'{update.message.chat.first_name}! {players["yeozhenhao"].username}{players["yeozhenhao"].taskstodo}')

    send_menu_Angel = [
        [InlineKeyboardButton(f"My Tasks", callback_data='mytasks')],
        [InlineKeyboardButton(f"Complete Tasks", callback_data='completetasks'),
         InlineKeyboardButton(f"Add Tasks", callback_data='addtasks')],
        [InlineKeyboardButton(f"Task info", callback_data='infotasks')],
        [InlineKeyboardButton(f"Feedback to Bot creator", callback_data='gamemastersupport')]
    ]
    reply_markup_Angel = InlineKeyboardMarkup(send_menu_Angel)
    update.message.reply_text(f'Hi {update.message.chat.first_name}! {messagesdualbot.HELP_TEXT_ANGEL}',
                              reply_markup=reply_markup_Angel, parse_mode=ParseMode.HTML)
    return CHOOSING



def help_command_ANGEL(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(messagesdualbot.HELP_TEXT_ANGEL)



@player.restricted
def reload_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /reloadchatids is issued."""
    PostgreSQLconnect.create_sql_players()
    PostgreSQLconnect.import_playertaskstodo_fromJSON_toSQL()
    logger.info(f'Player taskstodo have been imported from local JSON into SQL server')
    update.message.reply_text(f'Players taskstodo reloaded into taskstodo SQL!')

@player.restricted
def savechatids_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /savechatids is issued."""
    PostgreSQLconnect.saveplayertaskstodo_toSQL(players)
    logger.info(f'Player taskstodo have been saved in playertaskstodo SQL')
    update.message.reply_text(f'Player taskstodo are saved in playertaskstodo SQL!')

@player.restricted
def savechatids_toJSON_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /downloadchatids is issued."""
    PostgreSQLconnect.saveplayertaskstodo_toSQL(players)
    logger.info(f'Player chat ids have been saved in playerchatids SQL')
    PostgreSQLconnect.saveplayertaskstodo_fromSQL_toJSON()
    logger.info(f'Player taskstodo are downloaded into local JSON!')
    update.message.reply_text(f'Player taskstodo are downloaded into local JSON!')



'''
/mortal command is replaced with InlineKeyboardButton "Who is my mortal?". Ignore code below
'''


def viewmyTasks (update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(f"{messagesdualbot.YOUR_CURRENT_TASKS(playerName)}\n\n{messagesdualbot.START_AGAIN}")
    return ConversationHandler.END

def viewTasksinfo (update: Update, context: CallbackContext):
    update.callback_query.message.reply_text(f"messagesdualbot.gettasksinfo")
    return CHOOSING

def viewaddTasks (update: Update, context: CallbackContext):
    update.callback_query.message.reply_text(messagesdualbot.getaddTasksMessage)
    return ADDTASKS


def viewcompleteTasks (update: Update, context: CallbackContext):
    update.callback_query.message.reply_text(messagesdualbot.getcompleteTasksMessage)
    return REMOVETASKS

def sendaddTasks(update: Update, context: CallbackContext):
    playerName = update.message.chat.username.lower()
    words = update.message.text.split()
    x = words[0]
    y = words[1]
    update.message.reply_text(
        f"<b>{x}</b> {y}"
    )
    if update.message.text:
        try:
            words = update.message.text.split()
            tempdata = players[playerName].taskstodo
            tempdata[int(words[0])] = int(tempdata[int(words[0])]) + int(words[1])
            players[playerName].taskstodo = tempdata
            update.message.reply_text(
                f"<b>{playerName}</b> added task no. <b>{words[0]}</b> for <b>{words[0]}</b> times!\n\n"
                f"You may now click other buttons in the menu",
                parse_mode=ParseMode.HTML
            )
            logger.info(f"{playerName} added task no. {words[0]} for {words[0]} times!")
        except:
            update.message.reply_text(f"Sorry, please send messages in the correct format e.g. '1 1' if you wish to task no. 1 for one time.")
            return CHOOSING
    else:
        update.message.reply_text(
            f"Sorry, please send messages in text only.",
            parse_mode=ParseMode.HTML
        )

    return CHOOSING

def sendcompleteTasks(update: Update, context: CallbackContext):
    playerName = update.message.chat.username.lower()
    if update.message.text:
        try:
            words = update.message.text.split
            tempdata = players[playerName].taskstodo
            tempdata[int(words[0])] = int(tempdata[int(words[0])]) - int(words[1])
            players[playerName].taskstodo = tempdata
            update.message.reply_text(
                f"<b>{playerName}</b> completed task no.n <b>{words[0]}</b> for <b>{words[0]}</b> times!\n\n"
                f"You may now click other buttons in the menu",
                parse_mode=ParseMode.HTML
            )
            logger.info(f"{playerName} added task no. {words[0]} for {words[0]} times!")
        except:
            update.message.reply_text(f"Sorry, please send messages in the correct format e.g. '1 1' if you have completed task no. 1 one time.")
            return CHOOSING
    else:
        update.message.reply_text(
            f"Sorry, please send messages in text only.",
            parse_mode=ParseMode.HTML
        )

    return CHOOSING



'''
GAME MASTER SUPPORT
'''

angelbot = telegram.Bot(ANGEL_BOT_TOKEN)

def startGameMasterSupport (update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    if configdualbot.gamemasterchatid is None:
        update.callback_query.message.reply_text(f"Sorry the gamemaster is not available. Please try again later.")
        logger.info(messagesdualbot.getNotRegisteredLog(playerName, f"Failed to chat with GameMaster"))
        return CHOOSING

    update.callback_query.message.reply_text(messagesdualbot.getSupportMessage())
    return GAMEMASTERSUPPORT

'''
Note: All support texts will be sent to GameMaster through Mortal Bot
'''

def sendGameMasterAngelbot(update: Update, context: CallbackContext, bot=angelbot):
    playerName = update.message.chat.username.lower()
    if update.message.text:
        try:
            bot.send_message(
                text=f"<b> SUPPORT from @{update.message.chat.username} of chat_id {update.message.chat_id} using Angel Bot:</b>\n\n{update.message.text}",
                chat_id=configdualbot.gamemasterchatid,
                parse_mode=ParseMode.HTML
            )
        except:
            update.message.reply_text(f"Sorry the gamemaster is not available. Please try again later.")
            return CHOOSING
    else:
        sendNonTextMessage(update.message, bot, configdualbot.gamemasterchatid, ANGEL_BOT_TOKEN)
        bot.send_message(
            text=f"<b> SUPPORT Non-Text Message from @{update.message.chat.username} of chat_id {update.message.chat_id} using Angel Bot</b>",
            chat_id=configdualbot.gamemasterchatid,
            parse_mode=ParseMode.HTML
        )

    update.message.reply_text(messagesdualbot.MESSAGE_SENT_TO_GAMEMASTER)
    logger.info(f"{playerName} used Angel Bot & sent message to GameMaster")

    return CHOOSING




def cancel(update: Update, context: CallbackContext) -> int:
    logger.info(f"{update.message.chat.username} cancelled the conversation.")
    update.message.reply_text(
        'Process ended. Please type /start to chat again.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updaterAngel = Updater(ANGEL_BOT_TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dispatcherAngel = updaterAngel.dispatcher
    # on different commands - answer in Telegram
    dispatcherAngel.add_handler(CommandHandler("start", start_Angelbot))
    dispatcherAngel.add_handler(CommandHandler("help", help_command_ANGEL))
    dispatcherAngel.add_handler(CommandHandler("reloadtaskstodo", reload_command))
    dispatcherAngel.add_handler(CommandHandler("savetaskstodo", savechatids_command))
    dispatcherAngel.add_handler(CommandHandler("downloadtaskstodo", savechatids_toJSON_command))


    conv_handler_Angel = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_Angelbot),
            MessageHandler(~Filters.command, start_Angelbot),  ##putting ~Filters.all will cause an error
        ],
        states={
            CHOOSING:
                [
                    # CallbackQueryHandler(viewmyTasks, pattern='mytasks'),
                    # CallbackQueryHandler(viewcompleteTasks, pattern='completetasks'),
                    CallbackQueryHandler(viewaddTasks, pattern='addtasks'),
                    CallbackQueryHandler(viewTasksinfo, pattern='infotasks')
                    # CallbackQueryHandler(startGameMasterSupport, pattern='gamemastersupport') #### DO NOT ADD A , HERE
                ],
            # ADDTASKS: [MessageHandler(~Filters.command, sendaddTasks)],
            # REMOVETASKS: [MessageHandler(~Filters.command, sendcompleteTasks)],
            GAMEMASTERSUPPORT: [MessageHandler(~Filters.command, sendGameMasterAngelbot)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcherAngel.add_handler(conv_handler_Angel)

    # Start the Bot
    updaterAngel.start_polling()
    '''
    The next paragraph of codes replace "updater.start_polling()" 
    to enable listening to webhooks on heroku. See https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2 for information.
    '''

    # updaterAngel.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=ANGEL_BOT_TOKEN,
    #                       webhook_url=f'https://{herokuappname}.herokuapp.com/{ANGEL_BOT_TOKEN}')


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updaterAngel.idle()


if __name__ == '__main__':
    # try:
        main()
    # finally:
    #     PostgreSQLconnect.saveplayertaskstodo_toSQL(players)
    #     print(f'Player chat ids have been saved in playerchatids SQL')
    #     logger.info(f'Player chat ids have been saved in playerchatids SQL')