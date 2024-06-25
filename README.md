<div align="center">
<h1>Audiofiles Recognizer Bot<h1>
</div>

Audiofiles Recognizer Bot is a Telegram bot designed for speech-to-text conversion and track recognition using Shazam. This bot provides a convenient way to transcribe audio messages into text and identify music tracks.

<div align="center">
<h1>Features<h1>
</div>

- **Speech-to-Text Conversion:** Easily convert audio messages to text format.
- **Track Recognition:** Utilize Shazam operations to recognize music tracks.
- **Telegram Integration:** Seamlessly integrate with the Telegram messaging platform for user convenience.
- **User-friendly Interface:** Simple and intuitive interface for easy interaction.

<div align="center">
<h1>Installation<h1>
</div>

To deploy your own instance of Audiofiles Recognizer Bot, follow these steps:

1. **Clone the Repository and install Dependencies:**
- Note that this bot developed and tested with Python 3.11.
```
git clone https://github.com/your_username/Audiofiles-Recognizer-Bot.git
pip install -r requirements.txt
```

3. **Set Up Telegram Bot:**
- Create a new bot on Telegram using BotFather.
- Obtain the API token for your bot.
- Obtain Telgram API token for pyrogram here https://core.telegram.org/api/obtaining_api_id.
- Update the `Config/setup.env` file with your bot and app API token.
```
API_ID=00000000
API_HASH=aaaaaaaaaaaa
BOT_TOKEN=000000:AAAAAAAAAAAAAAAAAAAA
```

4. **Run the Bot with following .bat file or open Terminal in main folder and type this:**
```
python -m Bot
```
