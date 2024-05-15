<div align="center">
<h1>Audiofiles Recognizer Bot<h1>
</div>

Audiofiles Recognizer Bot is a Telegram bot designed for speech-to-text conversion and track recognition using Shazam. This bot provides a convenient way to transcribe audio messages into text and identify music tracks.

<div align="center">
<img src="https://cdn.discordapp.com/attachments/284756918331899904/1223997422158483546/aboba.png?ex=66456aae&is=6644192e&hm=d1fd3074cad91aadd36a6026474d9120f3a29b353d8e278f9b93a5f60fb0e437&" align="center" style="width: 75%" />
</div>

<div align="center">
<h1>Features<h1>
</div>

- **Speech-to-Text Conversion:** Easily convert audio messages to text format.
- **Track Recognition:** Utilize Shazam operations to recognize music tracks.
- **Telegram Integration:** Seamlessly integrate with the Telegram messaging platform for user convenience.
- **User-friendly Interface:** Simple and intuitive interface for easy interaction.

<div align="center">
<h1>Usage<h1>
</div>

1. **Start the Bot:** Start the bot by searching for "Audiofiles Recognizer Bot" on Telegram.
2. **Send Audio Messages:** Send audio messages to the bot for speech-to-text conversion.
3. **Identify Music Tracks:** Use the bot's Shazam operations to recognize music tracks.
4. **Enjoy the Results:** Receive the transcribed text or identified music track information directly within Telegram.

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
pause
```
