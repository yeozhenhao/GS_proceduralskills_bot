# Elgene's Angel and Mortals Dual Telegram Bots

Send anonymous messages between angels and mortals using two bots!

Start off anonymous except that your interests, two truths and one lie, and a self-intro are revealed to each other.

All you need is to collect the Telegram usernames, gender, interests, two truths and one lie, and their self-intro to start playing the game!


### Personal thoughts
- I felt that revealing the gender was important to contextualise the conversation
- Interests, two truths and one lie & self-intro were added to encourage people to break the ice & start the conversation.\
I felt these info were **essential** with the COVID19 restrictions & online learning, as students may never be able to physically meet each other.
- Also my gut feeling is that this bot can be just as effective as a matchmaking bot (but everyone gets two potential matches).\
NUS Aphrodite matchmaking uses interests, two truths one lie to break the ice too. But this bot still enables some form of anonymity (hopefully more exciting?).


### Accreditation
Special thanks to **Kingston Kuan** for his ***"How to make an Angels & Mortals Telegram Bot"*** guide! I have literally nil coding experience and his structured coding was easy to interpret and learn about the Telegram python module so I could work on it further. Please check out his article if you want to learn the basics of how this bot works! https://chatbotslife.com/building-a-chatbot-for-angel-mortal-5d389ab7acde



## What I added
1. Dual bot function:
- if you send a message to the Mortal Bot, your mortal receives it on the Angel Bot |\
if you send a message to the Angel Bot, your angel receives it on the Mortal Bot
####
- **SUPPORTS FORWARDING photos, stickers, documents, audio, videos, and animations:** dual bots were more tricky to forward messages than with a single bot. Initally only forwarding texts worked, so I added code to download these non-text messages directly from Telegram's servers so these could be forwarded too.
####
- **only requires /start on ONE of either bot to start receiving messages:** Alternatively, you may simply type any text and it will be the same as "/start"


2. Options to see Angel and Mortal's two truths one lie, self-introduction, and interests within the bots
- However, self-introduction was not added for Angels to prevent Mortals from identifying their Angels too easily
####
- Added "Who is my mortal?" option to see their mortal's Telegram username & gender
####
- Added read_csv functions to save the aforementioned properties (e.g. interests) into the Player objects

## Instructions

### How to format .csv file input & run bot
1. Put a header row in the following order

***"playerlist.csv" input file header columns:***
```
Player,Angel,Mortal,Gender,Interests,Twotruthsonelie,Introduction 
```
2. Ensure the data in the subequent rows matches the columns

***Data in "playerlist.csv" (excluding 1st-row headers):***
```
username1,username2,username3,Male,interests1,twotruthsonelie1,intro1
username2,username3,username1,Female,interests2,twotruthsonelie2,intro2
username3,username1,username2,Male,interests3,twotruthsonelie3,intro3
```
where the usernames are Telegram usernames without the "@".

3. Put the "playerlist.csv" in the root folder with all the other python scripts (e.g. dualbot.py)


4. Run dualbot.py 

### Environment variables required
MORTAL_BOT_TOKEN = os.environ['MORTAL_BOT_TOKEN']\
ANGEL_BOT_TOKEN = os.environ['ANGEL_BOT_TOKEN']\
PLAYERS_FILENAME = os.environ['PLAYERS_FILENAME']\
CHAT_ID_JSON = os.environ['CHAT_ID_JSON']\
ANGEL_ALIAS = os.environ['ANGEL_ALIAS']\
MORTAL_ALIAS = os.environ['MORTAL_ALIAS']

Calling 'Angels' & 'Mortals' too mainstream for you? Change them in the os.environ 'ANGEL_ALIAS' or 'MORTAL_ALIAS' to something else!\
_(Special thanks to Kingston Kuan for this idea)_

### If you only want a single bot purely for the anonymous messaging 
Run bot.py instead.

The files: **bot.py**, **config.py**, and **messages.py** are meant solely for the single bot and can be deleted if you only want the dual bot functionality.

Most of the code for the single bot is from **Kingston Kuan** (I have only made few minor changes and have not added the special functions of the dual bot).

### If you're looking for a matching algorithm to quickly match players for Angels & Mortals
Please see my other Python repository here:\
https://github.com/yeozhenhao/Angels_Mortals_Matching_algorithm