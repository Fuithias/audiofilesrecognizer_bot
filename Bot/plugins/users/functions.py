from asyncio import gather  # Importing gather from asyncio for concurrent execution
from cachetools import TTLCache  # Importing TTLCache for caching

from pydub import AudioSegment  # Importing AudioSegment from pydub for audio processing
from pydub.effects import normalize  # Importing normalize from pydub for audio normalization
from pydub.exceptions import CouldntDecodeError  # Importing CouldntDecodeError for handling decoding errors
from speech_recognition import Recognizer, AudioFile, UnknownValueError, RequestError  # Importing necessary classes from speech_recognition
from shazamio import Shazam  # Importing Shazam for audio recognition
from shazamio.exceptions import FailedDecodeJson  # Importing FailedDecodeJson for handling JSON decoding errors

from pyrogram import filters, enums  # Importing filters and enums from pyrogram for message filtering and enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup  # Importing necessary types from pyrogram
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, MessageNotModified  # Importing exceptions for handling bad requests

from Bot import bot, locales  # Importing bot and locales from the Bot module
from Bot.config import os  # Importing os
from Bot.helpers.decorators import run_sync_in_thread, run_rate_limiter  # Importing decorators from the Bot.helpers.decorators module
from Bot.database.database import insert_user, get_user_option, insert_chat, get_user_language  # Importing functions from the Bot.database.database module

shazam = Shazam()  # Initializing Shazam for audio recognition
recognized_tracks = TTLCache(1024, 43200)  # Initializing TTLCache for recognized tracks
TEMP_DIR = 'Temp'  # Setting temporary directory path


@bot.on_message(filters.voice | filters.audio | filters.document)
@run_rate_limiter  # Applying rate limiting decorator
async def get_media(_, update: Message):
    '''Handle incoming media messages.'''
    chat_id = update.chat.id
    message_id = update.id
    file_extension = await get_file_extension(update)
    file_path = f'{TEMP_DIR}/{chat_id}_{message_id}{file_extension}'
    
    if not os.path.isfile(file_path):
        await bot.download_media(update.audio or update.voice or update.document, file_path)
    
    await send_answer(_, update, chat_id, message_id, file_extension)


@run_sync_in_thread
def get_file_extension(update: Message) -> str:
    '''Get the file extension based on the type of media.'''
    if update.voice:
        return '.oga'
    if update.audio:
        return os.path.splitext(update.audio.file_name)[1]
    if update.document:
        return os.path.splitext(update.document.file_name)[1]


async def send_answer(_, update: Message, chat_id, message_id, file_extension):
    '''Send an answer based on user preferences.'''
    user_id = update.from_user.id
    user_language = update.from_user.language_code

    bot_language, speech_language, user_option = await gather(
        get_user_language(user_id, user_language, 'bot_language'),
        get_user_language(user_id, user_language, 'speech_language'),
        get_user_option(user_id)
    )

    await insert_chat(chat_id)
    await insert_user(user_id, update.from_user.username, bot_language, speech_language, user_option)

    await bot.send_chat_action(chat_id, enums.ChatAction.TYPING)

    if user_option == 0:
        try:
            message = await get_speech_to_text(chat_id, message_id, file_extension, bot_language, speech_language)
            await update.reply_text(message, quote=True)
        except MessageTooLong:
            messages = [message[i:i + 4096] for i in range(0, len(message), 4096)]
            for message_chunk in messages:
                await update.reply_text(message_chunk, quote=True)
        except MessageNotModified:
            pass
    elif user_option == 1:
        track_subject, track_link, track_id = await get_recognize_track(chat_id, message_id, file_extension, bot_language)

        if track_id:
            recognized_tracks[message_id] = track_id, track_subject, track_link
            message = track_subject + '\n' + track_link
            markup = await get_track_buttons(bot_language)
            await update.reply_text(message, quote=True, reply_markup=markup)
        else:
            await update.reply_text(track_subject, quote=True)


@run_sync_in_thread
def get_speech_to_text(chat_id, message_id, file_extension, bot_language, speech_language):
    '''Convert speech audio to text.'''
    file_path = f'{TEMP_DIR}/{chat_id}_{message_id}{file_extension}'
    audio_formats = {'.oga': 'ogg', '.wma': 'wmav2'}
    audio_format = audio_formats.get(file_extension, file_extension.replace('.', ''))

    try:
        # Attempt to load the audio file
        raw_sound = AudioSegment.from_file(file_path, codec=audio_format) if audio_format in ['opus', 'wmav2'] else AudioSegment.from_file(file_path, format=audio_format)
    except CouldntDecodeError:
        # Return format error message if decoding fails
        return locales[bot_language]['messages']['format_error']

    os.remove(file_path)  # Remove the audio file after loading

    normalized_sound = normalize(raw_sound, -10)  # Normalize the audio
    recognizer = Recognizer()  # Initialize the speech recognizer
    file_path = f'{TEMP_DIR}/{chat_id}_{message_id}.flac'

    if len(normalized_sound) > 38000:  # If audio length exceeds 38 seconds, split into chunks
        chunk_size = 25000
        recognized_text = ''

        for i, chunk in enumerate(normalized_sound[i:i + chunk_size] for i in range(0, len(normalized_sound), chunk_size)):
            chunk_file = f'{TEMP_DIR}/{chat_id}_{message_id}_{i}.flac'
            chunk.export(chunk_file, format='flac')  # Export the chunk as FLAC format

            with AudioFile(chunk_file) as source:
                try:
                    # Recognize speech from the chunk
                    text = recognizer.recognize_google(recognizer.record(source), language=speech_language, pfilter=1)
                    recognized_text += text
                except (UnknownValueError, RequestError) as error:
                    # Handle recognition errors
                    recognized_text += locales[bot_language]['messages']['recognition_fail'] if isinstance(error, UnknownValueError) else locales[bot_language]['messages']['recognition_error']

            os.remove(chunk_file)  # Remove the chunk file after processing

        return recognized_text
    else:
        try:
            # Export the normalized audio as FLAC format
            with normalized_sound.export(file_path, format='flac'):
                with AudioFile(file_path) as source:
                    # Recognize speech from the audio
                    recognized_text = recognizer.recognize_google(recognizer.record(source), language=speech_language, pfilter=1)
        except (UnknownValueError, RequestError) as error:
            # Handle recognition errors
            recognized_text = locales[bot_language]['messages']['recognition_fail'] if isinstance(error, UnknownValueError) else locales[bot_language]['messages']['recognition_error']
        finally:
            os.remove(file_path)  # Remove the temporary FLAC file

        return recognized_text


async def get_recognize_track(chat_id, message_id, file_extension, bot_language):
    '''Recognize music track from audio.'''
    file_path = f'{TEMP_DIR}/{chat_id}_{message_id}{file_extension}'
    recognized_json = await shazam.recognize(file_path)  # Use Shazam to recognize the track

    try:
        os.remove(file_path)  # Remove the audio file after recognition
    except FileNotFoundError:
        pass

    try:
        # Extract track information from the recognition result
        track_subject = recognized_json['track']['share']['subject']
        track_link = recognized_json['track']['share']['href']
        track_id = recognized_json['track']['key']
        return track_subject, track_link, track_id
    except KeyError:
        # Return failure message if track recognition fails
        fail_message = locales[bot_language]['messages']['recognize_fail']
        return fail_message, None, None


async def get_track_buttons(bot_language):
    '''Generate inline keyboard markup for track options.'''
    buttons = ['track_about', 'track_lyrics', 'track_similar']
    buttons_text = [locales[bot_language]['buttons'][btn] for btn in buttons]
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text, f'{btn}_button') for text, btn in zip(buttons_text, buttons)]])
    return markup