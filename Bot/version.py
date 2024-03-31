import sys  # Importing the sys module for system-related functionality
from pyrogram import __version__ as pyrogram_version  # Importing version information from the pyrogram module

# Obtaining the current Python version and converting it to a string
python_version = '.'.join(map(str, sys.version_info[:3]))
# Defining the version of the bot
bot_version = '12.5.1'