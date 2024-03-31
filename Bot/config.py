import os  # Importing the os module for interacting with the operating system
from dotenv import load_dotenv  # Importing load_dotenv function from dotenv module for loading environment variables

# Loading environment variables from the setup.env file
load_dotenv('Config/setup.env')
# Extracting API_ID from environment variables and converting it to an integer
API_ID = int(os.getenv('API_ID'))
# Extracting API_HASH from environment variables
API_HASH = os.getenv('API_HASH')
# Extracting BOT_TOKEN from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')