from Bot.logging import logger  # Importing the logger function from Bot.logging module
from Bot import bot  # Importing the bot instance from the Bot module

# Getting the logger for the current module and logging an informational message
logger('Bot').info('Client successfully initiated....')
# Running the bot
bot.run()