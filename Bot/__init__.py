import json  # Importing the JSON module for working with JSON data
from winloop import install  # Importing the install function from the winloop module
from asyncio import get_event_loop, new_event_loop, set_event_loop  # Importing functions related to asyncio event loops

from pyrogram import Client  # Importing the Client class from the pyrogram module

from Bot import config  # Importing configuration settings from the Bot module
from Bot.database.database import create_database  # Importing the create_database function from the Bot.database.database module
from Bot.logging import logger  # Importing the logger function from the Bot.logging module

# Setting up logging
log = logger(__name__)
# Logging the initiation of the program client
log.info('Starting program client....')
install()  # Installing winloop
# Setting up the event loop
log.info('Setting up event loop....')
loop = get_event_loop() if 'running' in locals() else new_event_loop()
set_event_loop(loop)
# Connecting to the database
log.info('Connecting to database....')
create_database()
# Loading locales from a JSON file
log.info('Loading locales....')
with open('Config/locales.json', 'r', encoding='utf8') as locales_json:
    locales = json.load(locales_json)
# Initiating the client
log.info('Initiating the client....')
plugins = dict(root='Bot/plugins')
bot = Client('Bot', config.API_ID, config.API_HASH, bot_token=config.BOT_TOKEN, plugins=plugins)