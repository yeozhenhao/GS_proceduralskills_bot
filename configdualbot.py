import os

ANGEL_BOT_TOKEN = os.environ['ANGEL_BOT_TOKEN']
# PLAYERS_FILENAME = os.environ['PLAYERS_FILENAME']
TASKSTODO_CSV = os.environ['TASKSTODO_CSV']
herokuappname = os.environ['herokuappname']  ##for bot to listen to heroku Webhook
dbhost = os.environ['dbhost']
dbname = os.environ['dbname']  ##for connecting to PostgreSQL database on heroku
dbuser = os.environ['dbuser']
dbpassword = os.environ['dbpassword']
gamemasterchatid = os.environ['gamemasterchatid']
# ANGEL_BOT_ID = os.environ['ANGEL_BOT_ID'] ##not used atm, was for send_polls
# MORTAL_BOT_ID = os.environ['MORTAL_BOT_ID'] ##not used atm, was for send_polls
