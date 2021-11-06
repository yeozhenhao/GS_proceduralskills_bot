import logging

import player
import messagesdualbot
import datetime
import collections
import PostgreSQLconnect

import configdualbot
import telegram
from telegram import ParseMode
import dload  ##important for parsing JSON htmls; to enable bot forwarding of images between bots
import requests

import os ##for heroku setup
PORT = int(os.environ.get('PORT', '8443')) ##for heroku setup. See https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku


class Response():  ##Class for Telegram files
    def __init__(self):
        self.ok = None
        self.result = {}
        self.result["file_id"] = None
        self.result["file_unique_id"] = None
        self.result["file_size"] = None
        self.result["file_path"] = None


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler

GAMEMASTERSUPPORT, CHOOSING, ANGEL, MORTAL = range(4)

# Enable logging
logging.basicConfig(
    filename=f'logs/{datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")}.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ANGEL_BOT_TOKEN = configdualbot.ANGEL_BOT_TOKEN
MORTAL_BOT_TOKEN = configdualbot.MORTAL_BOT_TOKEN
herokuappname = configdualbot.herokuappname

players = collections.defaultdict(player.Player)
PostgreSQLconnect.loadPlayers_fromSQL(players)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start_Angelbot(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    playerName = update.message.chat.username.lower()

    if players[playerName].username is None:
        update.message.reply_text(messagesdualbot.NOT_REGISTERED)
        return

    players[playerName].chat_id = update.message.chat.id

    if players[playerName].chat_id is None:  ##just in case
        update.message.reply_text(messagesdualbot.ERROR_CHAT_ID)
        return

    logger.info(f'{playerName} started the bot with chat_id {players[playerName].chat_id}')

    send_menu_Angel = [
        [InlineKeyboardButton(f"Talk to my {configdualbot.ANGEL_ALIAS}", callback_data='messageangel')],
        [InlineKeyboardButton(f"Who is my {configdualbot.ANGEL_ALIAS}?", callback_data='whoismyangel'),
         InlineKeyboardButton(f"My {configdualbot.ANGEL_ALIAS}'s interests", callback_data='angelinterests')],
        [InlineKeyboardButton(f"My {configdualbot.ANGEL_ALIAS}'s Two truths and one lie", callback_data='angeltwotruthsonelie')],
        [InlineKeyboardButton(f"Feedback to Game Master", callback_data='gamemastersupport')],
    ]
    reply_markup_Angel = InlineKeyboardMarkup(send_menu_Angel)
    update.message.reply_text(f'Hi {update.message.chat.first_name}! {messagesdualbot.HELP_TEXT_ANGEL}',
                              reply_markup=reply_markup_Angel)

    return CHOOSING


def start_Mortalbot(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    playerName = update.message.chat.username.lower()
    if players[playerName].username is None:
        update.message.reply_text(messagesdualbot.NOT_REGISTERED)
        return  ##returns whatever state it previously was at

    players[playerName].chat_id = update.message.chat.id

    if players[playerName].chat_id is None:  ##just in case
        update.message.reply_text(messagesdualbot.ERROR_CHAT_ID)
        return  ##returns whatever state it previously was at

    logger.info(f'{playerName} started the bot with chat_id {players[playerName].chat_id}')

    send_menu_Mortal = [
        [InlineKeyboardButton(f"Talk to my {configdualbot.MORTAL_ALIAS}", callback_data='messagemortal')],
        ##NOTE: Do not put "mortal" as callback_data, or else other callback_data starting with "mortal" will not work anymore.
        [InlineKeyboardButton(f"Who is my {configdualbot.MORTAL_ALIAS}?", callback_data='whoismymortal'),
         InlineKeyboardButton(f"My {configdualbot.MORTAL_ALIAS}'s interests", callback_data='mortalinterests')],
        [InlineKeyboardButton(f"My {configdualbot.MORTAL_ALIAS}'s Two truths and one lie",
                              callback_data='mortaltwotruthsonelie')],
        [InlineKeyboardButton(f"My {configdualbot.MORTAL_ALIAS}'s self-intro", callback_data='mortalintroduction')],
        [InlineKeyboardButton(f"Feedback to Game Master", callback_data='gamemastersupport')],
    ]
    reply_markup_Mortal = InlineKeyboardMarkup(send_menu_Mortal)
    update.message.reply_text(f'Hi {update.message.chat.first_name}! {messagesdualbot.HELP_TEXT_MORTAL}',
                              reply_markup=reply_markup_Mortal)

    return CHOOSING


def help_command_ANGEL(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(messagesdualbot.HELP_TEXT_ANGEL)

def help_command_MORTAL(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(messagesdualbot.HELP_TEXT_MORTAL)


@player.restricted
def reload_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /reloadchatids is issued."""
    PostgreSQLconnect.create_sql_players()
    PostgreSQLconnect.import_players_from_csv()
    logger.info(f'Player data has been imported from local csv into SQL server')
    PostgreSQLconnect.import_playerchatids_fromJSON_toSQL()
    logger.info(f'Player chat ids have been imported from local JSON into SQL server')
    update.message.reply_text(f'Players reloaded into SQL!')

@player.restricted
def savechatids_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /savechatids is issued."""
    PostgreSQLconnect.saveplayerschatids_toSQL(players)
    logger.info(f'Player chat ids have been saved in playerchatids SQL')
    update.message.reply_text(f'Player chat ids are saved in playerchatids SQL!')

@player.restricted
def savechatids_toJSON_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /downloadchatids is issued."""
    PostgreSQLconnect.saveplayerschatids_toSQL(players)
    logger.info(f'Player chat ids have been saved in playerchatids SQL')
    PostgreSQLconnect.saveplayerchatids_fromSQL_toJSON()
    logger.info(f'Player chat ids are downloaded into local JSON!')
    update.message.reply_text(f'Player chat ids are downloaded into local JSON!')



'''
/mortal command is replaced with InlineKeyboardButton "Who is my mortal?". Ignore code below
'''


# def mortal_command(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /mortal is issued."""
#     playerName = update.message.chat.username.lower()
#     update.message.reply_text(f"Your mortal is @{players[playerName].mortal.username}, Gender: {players[playerName].mortal.gender}")


def startAngel(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    if players[playerName].angel.chat_id is None:
        update.callback_query.message.reply_text(messagesdualbot.getBotNotStartedMessage(configdualbot.ANGEL_ALIAS))
        logger.info(messagesdualbot.getNotRegisteredLog(configdualbot.ANGEL_ALIAS, playerName,
                                                        players[playerName].angel.username))
        return CHOOSING

    update.callback_query.message.reply_text(messagesdualbot.getPlayerMessage(configdualbot.ANGEL_ALIAS))
    return ANGEL


def whoismyAngel(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"That's for you to find out! But I can tell you the Gender: <b>{players[playerName].angel.gender}</b>",
        parse_mode=ParseMode.HTML)
    return CHOOSING


def angelInterests(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"<u>Your {configdualbot.ANGEL_ALIAS}'s interests:</u>\n\n{players[playerName].angel.interests}",
        parse_mode=ParseMode.HTML)
    return CHOOSING


def angelTwotruthsonelie(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"<b>Your {configdualbot.ANGEL_ALIAS}'s Two truths and one lie:</b>\n\n{players[playerName].angel.twotruthsonelie}",
        parse_mode=ParseMode.HTML)
    return CHOOSING


def startMortal(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    if players[playerName].mortal.chat_id is None:
        update.callback_query.message.reply_text(messagesdualbot.getBotNotStartedMessage(configdualbot.MORTAL_ALIAS))
        logger.info(messagesdualbot.getNotRegisteredLog(configdualbot.MORTAL_ALIAS, playerName,
                                                        players[playerName].mortal.username))
        return CHOOSING

    update.callback_query.message.reply_text(messagesdualbot.getPlayerMessage(configdualbot.MORTAL_ALIAS))
    return MORTAL


def whoismyMortal(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"Your {configdualbot.MORTAL_ALIAS} is @{players[playerName].mortal.username}, Gender: <b>{players[playerName].mortal.gender}</b>",
        parse_mode=ParseMode.HTML)
    return CHOOSING


def mortalInterests(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"<u>Your {configdualbot.MORTAL_ALIAS}'s interests:</u>\n\n{players[playerName].mortal.interests}",
        parse_mode=ParseMode.HTML)
    return CHOOSING


def mortalTwotruthsonelie(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"<b>Your {configdualbot.MORTAL_ALIAS}'s Two truths and one lie:</b>\n\n{players[playerName].mortal.twotruthsonelie}",
        parse_mode=ParseMode.HTML)
    return CHOOSING


'''
I decided to only let angels see the introduction of mortals but not vice versa to prevent easy identification of angels to mortals.
'''


def mortalIntroduction(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    update.callback_query.message.reply_text(
        f"<b>Your {configdualbot.MORTAL_ALIAS}'s self-intro:</b>\n\n{players[playerName].mortal.introduction}",
        parse_mode=ParseMode.HTML)
    return CHOOSING


'''
message.photo example output:
[<telegram.files.photosize.PhotoSize object at 0x000001E862EC8880>, <telegram.files.photosize.PhotoSize object at 0x000001E862EC8AC0>, <telegram.files.photosize.PhotoSize object at 0x000001E862EC89A0>, <telegram.files.photosize.PhotoSize object at 0x000001E862EC8940>]
message.photo[-1] example output:
{'file_size': 126249, 'width': 720, 'file_unique_id': 'AQAD-7AxG9hWWFd-', 'file_id': 'AgACAgUAAxkBAAICG2FrmmQrkdsQZXXatT32MAG6_Z71AAL7sDEb2FZYVwZB8PbnNsibAQADAgADeQADIQQ', 'height': 1280}
'''


def grabResponse(file_id, token):
    response = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    logger.info(f"{file_id} // {response}")
    j = dload.json(response)
    logger.info(dload.json(response))
    filepath = j["result"]["file_path"]
    htmllink = f"https://api.telegram.org/file/bot{token}/{filepath}"
    response2 = requests.get(htmllink)  ##Somehow, passing the html link into photo does NOT work.
    # Use response2.content to get the string, then pass the bytes into the argument instead! :)
    logger.info(f"{filepath} // {htmllink}")
    return response2, filepath


def sendNonTextMessage(message, bot, chat_id, token):
    if message.photo:
        fileid = message.photo[-1]["file_id"]
        response2, filepath = grabResponse(fileid, token)
        bot.send_photo(
            photo=response2.content,
            caption=message.caption,
            chat_id=chat_id
        )
    elif message.sticker:
        bot.send_sticker(
            sticker=message.sticker,
            chat_id=chat_id
        )
    elif message.document:
        fileid = message.document["file_id"]
        response2, filepath = grabResponse(fileid, token)
        response2.encoding = 'utf-8'  ##explicit encoding by setting .encoding before accessing .text
        bot.send_document(
            document=response2.content,
            filename=f"{filepath.split('/')[-1]}",
            ##sending in bytes loses the file name & file type. Not perfect, but this is probably the best solution.
            caption=message.caption,
            chat_id=chat_id
        )
    elif message.video:
        fileid = message.video["file_id"]
        response2, filepath = grabResponse(fileid, token)
        bot.send_video(
            video=response2.content,
            caption=message.caption,
            chat_id=chat_id
        )
    elif message.video_note:
        fileid = message.video_note["file_id"]
        response2, filepath = grabResponse(fileid, token)
        bot.send_video_note(
            video_note=response2.content,
            chat_id=chat_id
        )
    elif message.voice:
        fileid = message.voice["file_id"]
        response2, filepath = grabResponse(fileid, token)
        bot.send_voice(
            voice=response2.content,
            chat_id=chat_id
        )
    elif message.audio:
        fileid = message.audio["file_id"]
        response2, filepath = grabResponse(fileid, token)
        bot.send_audio(
            audio=response2.content,
            chat_id=chat_id
        )
    elif message.animation:
        fileid = message.animation["file_id"]
        response2, filepath = grabResponse(fileid, token)
        bot.send_animation(
            animation=response2.content,
            chat_id=chat_id
        )

    '''
    Fowarding polls probably doesn't work for now, ignore the code below
    '''
    # elif message.poll:
    #     tempPoll = telegram.Poll(chat_id = None,
    #                             question = None,
    #                             options = None,
    #                             is_anonymous = None,
    #                             type = None,
    #                             allows_multiple_answers = None,
    #                             correct_option_id = None,
    #                             explanation = None,
    #                             open_period=None,
    #                             close_date= None,
    #                             id = None,
    #                             total_voter_count= None,
    #                             is_closed=None,
    #                  )
    #     tempPoll = message.poll
    #     tempOptions = []
    #     for x in message.poll.options:
    #         y = json.loads(x)
    #         tempOptions.append(y)
    #         logger.info (x, y)
    #     bot.send_poll(chat_id = chat_id,
    #                   question = tempPoll.question,
    #                   options = tempOptions,
    #                   is_anonymous = tempPoll.is_anonymous,
    #                   type = tempPoll.type,
    #                   allows_multiple_answers = tempPoll.allows_multiple_answers,
    #                   correct_option_id = tempPoll.correct_option_id,
    #                   explanation = tempPoll.explanation,
    #                   open_period=tempPoll.open_period,
    #                   close_date=tempPoll.close_date,
    #                   )


angelbot = telegram.Bot(ANGEL_BOT_TOKEN)
mortalbot = telegram.Bot(MORTAL_BOT_TOKEN)

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

def sendGameMasterMortalbot(update: Update, context: CallbackContext, bot=mortalbot):
    playerName = update.message.chat.username.lower()
    if update.message.text:
        try:
            bot.send_message(
                text=f"<b> SUPPORT from @{update.message.chat.username} of chat_id {update.message.chat_id} using Mortal Bot:</b>\n\n{update.message.text}",
                chat_id=configdualbot.gamemasterchatid,
                parse_mode=ParseMode.HTML
            )
        except:
            update.message.reply_text(f"Sorry the gamemaster is not available. Please try again later.")
            return CHOOSING
    else:
        sendNonTextMessage(update.message, bot, configdualbot.gamemasterchatid, MORTAL_BOT_TOKEN)
        bot.send_message(
            text=f"<b> SUPPORT Non-Text Message from @{update.message.chat.username} of chat_id {update.message.chat_id} using Mortal Bot</b>",
            chat_id=configdualbot.gamemasterchatid,
            parse_mode=ParseMode.HTML
        )

    update.message.reply_text(messagesdualbot.MESSAGE_SENT_TO_GAMEMASTER)
    logger.info(f"{playerName} used Mortal Bot & sent message to GameMaster")

    return CHOOSING

def sendGameMasterAngelbot(update: Update, context: CallbackContext, bot=mortalbot):
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

def sendAngel(update: Update, context: CallbackContext, bot=mortalbot):
    playerName = update.message.chat.username.lower()
    # logger.info(f'{context.bot}')
    if update.message.text:
        try:
            bot.send_message(
                text=update.message.text,
                chat_id=players[playerName].angel.chat_id
            )
        except:
            update.message.reply_text(messagesdualbot.STOPPED_BOT(configdualbot.ANGEL_ALIAS))
            return CHOOSING
    else:
        sendNonTextMessage(update.message, bot, players[playerName].angel.chat_id, ANGEL_BOT_TOKEN)

    update.message.reply_text(messagesdualbot.MESSAGE_SENT)

    logger.info(
        messagesdualbot.getSentMessageLog(configdualbot.ANGEL_ALIAS, playerName, players[playerName].angel.username))

    return ANGEL


def sendMortal(update: Update, context: CallbackContext, bot=angelbot):
    playerName = update.message.chat.username.lower()
    # logger.info(f'{context.bot}') ##to find out the current telegram.Bot Object being used
    if update.message.text:
        try:
            bot.send_message(
                text=update.message.text,
                chat_id=players[playerName].mortal.chat_id
            )
        except:
            update.message.reply_text(messagesdualbot.STOPPED_BOT(configdualbot.MORTAL_ALIAS))
            return CHOOSING
    else:
        sendNonTextMessage(update.message, bot, players[playerName].mortal.chat_id, MORTAL_BOT_TOKEN)

    update.message.reply_text(messagesdualbot.MESSAGE_SENT)

    logger.info(
        messagesdualbot.getSentMessageLog(configdualbot.MORTAL_ALIAS, playerName, players[playerName].mortal.username))

    return MORTAL


def cancel(update: Update, context: CallbackContext) -> int:
    logger.info(f"{update.message.chat.username} canceled the conversation.")
    update.message.reply_text(
        'Sending message cancelled. Please type /start to chat again.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updaterMortal = Updater(MORTAL_BOT_TOKEN, use_context=True)
    # updaterAngel = Updater(ANGEL_BOT_TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dispatcherMortal = updaterMortal.dispatcher
    # dispatcherAngel = updaterAngel.dispatcher
    # on different commands - answer in Telegram
    # dispatcherMortal.add_handler(CommandHandler("start", start_Mortal))
    dispatcherMortal.add_handler(CommandHandler("help", help_command_MORTAL))
    dispatcherMortal.add_handler(CommandHandler("reloadchatids", reload_command))
    dispatcherMortal.add_handler(CommandHandler("savechatids", savechatids_command))
    dispatcherMortal.add_handler(CommandHandler("downloadchatids", savechatids_toJSON_command))
    # dispatcherMortal.add_handler(CommandHandler("mortal", mortal_command))

    # dispatcherAngel.add_handler(CommandHandler("start", start_Angel))
    # dispatcherAngel.add_handler(CommandHandler("help", help_command_ANGEL))
    # dispatcherAngel.add_handler(CommandHandler("reloadchatids", reload_command))
    # dispatcherAngel.add_handler(CommandHandler("savechatids", savechatids_command))
    # dispatcherAngel.add_handler(CommandHandler("downloadchatids", savechatids_toJSON_command))


    conv_handler_Angel = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_Angelbot),
            MessageHandler(~Filters.command, start_Angelbot),  ##putting ~Filters.all will cause an error
        ],
        states={
            CHOOSING:
                [
                    CallbackQueryHandler(startAngel, pattern='messageangel'),
                    CallbackQueryHandler(whoismyAngel, pattern='whoismyangel'),
                    CallbackQueryHandler(angelInterests, pattern='angelinterests'),
                    CallbackQueryHandler(angelTwotruthsonelie, pattern='angeltwotruthsonelie'),
                    CallbackQueryHandler(startGameMasterSupport, pattern='gamemastersupport'),
                ],
            ANGEL: [MessageHandler(~Filters.command, sendAngel)],
            GAMEMASTERSUPPORT: [MessageHandler(~Filters.command, sendGameMasterAngelbot)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    conv_handler_Mortal = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_Mortalbot),
            MessageHandler(~Filters.command, start_Mortalbot),  ##putting ~Filters.all will cause an error
        ],
        states={
            CHOOSING:
                [
                    CallbackQueryHandler(startMortal, pattern='messagemortal'),
                    CallbackQueryHandler(whoismyMortal, pattern='whoismymortal'),
                    CallbackQueryHandler(mortalInterests, pattern='mortalinterests'),
                    CallbackQueryHandler(mortalTwotruthsonelie, pattern='mortaltwotruthsonelie'),
                    CallbackQueryHandler(mortalIntroduction, pattern='mortalintroduction'),
                    CallbackQueryHandler(startGameMasterSupport, pattern='gamemastersupport'),
                ],
            MORTAL: [MessageHandler(~Filters.command, sendMortal)],
            GAMEMASTERSUPPORT: [MessageHandler(~Filters.command, sendGameMasterMortalbot)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcherMortal.add_handler(conv_handler_Mortal)
    # dispatcherAngel.add_handler(conv_handler_Angel)

    # Start the Bot
    # updaterMortal.start_polling()
    # updaterAngel.start_polling()
    '''
    The next paragraph of codes replace "updater.start_polling()" 
    to enable listening to webhooks on heroku. See https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2 for information.
    '''
    updaterMortal.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=MORTAL_BOT_TOKEN,
                          webhook_url=f'https://{herokuappname}.herokuapp.com/{MORTAL_BOT_TOKEN}')

    # updaterAngel.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=ANGEL_BOT_TOKEN,
    #                       webhook_url=f'https://{herokuappname}.herokuapp.com/{ANGEL_BOT_TOKEN}')


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updaterMortal.idle()
    # updaterAngel.idle()


if __name__ == '__main__':
    try:
        main()
    finally:
        PostgreSQLconnect.saveplayerschatids_toSQL(players)
        print(f'Player chat ids have been saved in playerchatids SQL')
        logger.info(f'Player chat ids have been saved in playerchatids SQL')