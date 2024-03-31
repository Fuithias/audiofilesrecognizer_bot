from asyncio import gather # Importing gather from asyncio for concurrent execution
from requests.exceptions import RequestException
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

from pyrogram import filters, enums # Importing filters and enums from pyrogram for message filtering and enums
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message  # Importing necessary types from pyrogram
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified, MessageEmpty # Importing exceptions for handling bad requests

from Bot import bot, locales # Importing bot and locales from the Bot module
from Bot.helpers.decorators import run_rate_limiter # Importing decorator from the Bot.helpers.decorators module
from Bot.plugins.users.functions import recognized_tracks, shazam, get_track_buttons, FailedDecodeJson # Importing recognized tracks functionality related
from Bot.database.database import insert_chat, insert_user, get_user_option, get_user_language # Importing functions from the Bot.database.database module
from Bot.version import python_version, bot_version, pyrogram_version # Importing versions information


async def get_message_info(update: Message):
    '''Function to gather information from a message'''
    chat_id = update.chat.id
    user = update.from_user
     # Gather user information asynchronously
    bot_language, speech_language, user_option = await gather(
        get_user_language(user.id, user.language_code, 'bot_language'),
        get_user_language(user.id, user.language_code, 'speech_language'),
        get_user_option(user.id)
    )
    # Insert chat and user information into the database
    await gather(
        insert_chat(chat_id),
        insert_user(user.id, user.username, bot_language, speech_language, user_option),
        bot.send_chat_action(chat_id, enums.ChatAction.TYPING)
    )

    return bot_language, speech_language


@bot.on_message(filters.command(['start']))
@run_rate_limiter
async def get_start(_, update: Message):
    '''Command handler for /start command'''
    bot_language, speech_language = await get_message_info(update)
    message, markup = await get_start_content(bot_language, speech_language)
    await update.reply_text(message, quote=True, reply_markup=markup)


@bot.on_message(filters.command(['help']))
@run_rate_limiter
async def get_help(_, update: Message):
    '''Command handler for /help command'''
    bot_language, _ = await get_message_info(update)
    message, markup = await get_help_content(bot_language)
    await update.reply_text(message, quote=True, reply_markup=markup)


@bot.on_message(filters.text & filters.private & ~filters.command(['start']) & ~filters.command(['help']))
@run_rate_limiter
async def get_echo(_, update: Message):
    '''Handler for echoing text messages'''
    bot_language, _ = await get_message_info(update)
    echo_message = locales[bot_language]['messages']['echo']
    await update.reply_text(echo_message, quote=True)


async def get_start_content(bot_language, speech_language):
    '''Function to get content for /start command'''
    message = (
        f"{locales[bot_language]['messages']['start']}\n{locales[bot_language]['messages']['bot_language']}"
        f"{locales['origin'][bot_language]}{locales[bot_language][bot_language]}\n{locales[bot_language]['messages']['speech_language']}"
        f"{locales['origin'][speech_language]}{locales[bot_language][speech_language]}"
    )
    buttons_text = ['language', 'actions', 'about']
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(locales[bot_language]['buttons'][btn], f'{btn}_button')] for btn in buttons_text
    ])
    return message, markup


async def get_help_content(bot_language):
    '''Function to get content for /help command'''
    message = locales[bot_language]['messages']['about'].format(python_version, pyrogram_version, bot_version)
    back_button = [InlineKeyboardButton(locales[bot_language]['buttons']['back'], 'back_button')]
    markup = InlineKeyboardMarkup([back_button])
    return message, markup


async def get_languages(languages, bot_language, update_data):
    '''Function to get languages from locales json'''
    language_pairs = (languages[i:i+2] for i in range(0, len(languages), 2))
    markup = []
    for pair in language_pairs:
        row = [InlineKeyboardButton(locales['origin'][lang] + locales[bot_language][lang], lang + update_data) for lang in pair]
        markup.append(row)
    markup.append([InlineKeyboardButton(locales[bot_language]['buttons']['back'], 'language_button')])
    return InlineKeyboardMarkup(markup)


async def callback_answer(update: CallbackQuery, message, markup):
    '''Asynchronous function to handle callback query answer'''
    try:
        # Attempt to edit the message with the provided message and markup
        await update.edit_message_text(message, reply_markup=markup)
    except MessageNotModified:
        # Ignore if the message is not modified
        pass
    finally:
        # Send a callback query answer
        await update.answer()


@bot.on_callback_query(filters.regex('_button'))
@run_rate_limiter
async def bot_callbacks(_, update: CallbackQuery):
    '''Callback query handler for bot-related actions'''
    # Extract necessary information from the callback query
    user = update.from_user
    chat = update.message.chat
    reply_to_message = update.message.reply_to_message
    # Extract user and chat information
    user_id = user.id
    user_username = user.username
    user_language = user.language_code
    chat_id = chat.id
    # Gather user preferences and update database
    bot_language, speech_language, user_option = await gather(
        get_user_language(user_id, user_language, 'bot_language'),
        get_user_language(user_id, user_language, 'speech_language'),
        get_user_option(user_id)
    )
    # Inser user and chat if new
    await gather(
        insert_chat(chat_id),
        insert_user(user_id, user_username, bot_language, speech_language, user_option)
    )
    # Check if the same user send message and tap on buttons
    if reply_to_message.from_user.id != user_id:
        message = locales[bot_language]['messages']['command']
        await update.answer(message, show_alert=True)
    # Returns to /start menu
    if update.data == 'back_button':
        message, markup = await get_start_content(bot_language, speech_language)
        return await callback_answer(update, message, markup)
    # Returns to /help menu
    elif update.data == 'about_button':
        message, markup = await get_help_content(bot_language)
        return await callback_answer(update, message, markup)
    # Provide actions menu
    elif update.data == 'actions_button':
        buttons = ['speech_to_text', 'recognize_track', 'back']
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(locales[bot_language]['buttons'][btn], f'{btn}_button') for btn in buttons[:-1]],
            [InlineKeyboardButton(locales[bot_language]['buttons'][buttons[-1]], 'back_button')]
        ])
        message = locales[bot_language]['messages']['actions']
        return await callback_answer(update, message, markup)
    # Check what option is choose
    elif update.data in {'speech_to_text_button', 'recognize_track_button'}:
        action_type = update.data.replace('_button', '')
        message = locales[bot_language]['messages'][action_type]
        user_option = 0 if action_type == 'speech_to_text' else 1
        tasks = [
            insert_user(user_id, user_username, bot_language, speech_language, user_option),
            update.answer(message, show_alert=True)
        ]
        start_message, start_markup = await get_start_content(bot_language, speech_language)
        tasks.append(update.edit_message_text(start_message, reply_markup=start_markup))
        await gather(*tasks)
        return
    # Provide language menu that has bot and speech options
    elif update.data == 'language_button':
        buttons = ['bot_language', 'speech_language', 'back']
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(locales[bot_language]['buttons'][btn], f'{btn}_button')] for btn in buttons[:-1]
        ] + [
            [InlineKeyboardButton(locales[bot_language]['buttons'][buttons[-1]], 'back_button')]
        ])
        message = locales[bot_language]['messages']['actions']
        return await callback_answer(update, message, markup)
    # Check what option is choose for language changing and provide all supported languages
    elif update.data in {'bot_language_button', 'speech_language_button'}:
        message_key = 'bot_language' if update.data == 'bot_language_button' else 'speech_language'
        message = locales[bot_language]['buttons'][message_key]
        languages = list(locales['origin'].keys()) if message_key == 'bot_language' else [lang for lang in locales['origin'].keys() if lang not in locales['speechless']]
        update_data = 'lang_button' if message_key == 'bot_language' else 'langrec_button'
        message = f"{message}.\n{locales[bot_language]['messages']['language']}"
        markup = await get_languages(languages, bot_language, update_data)
        return await callback_answer(update, message, markup)
    # Check what type of language is choose and changing that
    elif 'lang_button' in update.data or 'langrec_button' in update.data:
        lang_type = 'bot_language' if 'lang_button' in update.data else 'speech_language'
        language = update.data.replace('lang_button', '') if lang_type == 'bot_language' else update.data.replace('langrec_button', '')
        if lang_type == 'bot_language':
            bot_language = language
        else:
            speech_language = language
        message = f"{locales[bot_language]['messages'][lang_type]}{locales['origin'][language]}{locales[bot_language][language]}"
        await gather(
            insert_user(user_id, user_username, bot_language, speech_language, user_option),
            update.answer(message, show_alert=True)
        )
        message, markup = await get_start_content(bot_language, speech_language)
        return await callback_answer(update, message, markup)
    # Returns to track menu
    elif update.data == 'track_button':
        track_id, track_subject, track_link = recognized_tracks.get(update.message.reply_to_message.id, (None, None, None))
        try:
            if not track_id:
                message = locales[bot_language]['messages']['unavailable']
                return await update.answer(message, show_alert=True)
            message = f'{track_subject}\n{track_link}'
            markup = await get_track_buttons(bot_language)
            return await callback_answer(update, message, markup)
        except MessageEmpty:
            message = locales[bot_language]['messages']['unavailable']
            return await update.answer(message, show_alert=True)
    # Provide track album information
    elif update.data == 'track_about_button':
        track_id, track_subject, track_link = recognized_tracks.get(update.message.reply_to_message.id, (None, None, None))
        if not track_id:
            message = locales[bot_language]['messages']['unavailable']
            return await update.answer(message, show_alert=True)

        try:
            message = f'{track_subject}\n{track_link}'
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(locales[bot_language]['buttons']['back'], 'track_button')]])
            about_json = await shazam.track_about(track_id)
            album_text = ''
            album_text = ' '.join(item['text'] for i, item in enumerate(about_json.get('sections', [{}])[0].get('metadata', [])) if i == 0 or (album_text := ' '.join([album_text, item['text']])))
            message += f'\n{album_text}'
            return await callback_answer(update, message, markup)
        except (KeyError, FailedDecodeJson):
            message = locales[bot_language]['messages']['unavailable']
            return await update.answer(message, show_alert=True)
    # Provide track lyrics
    elif update.data == 'track_lyrics_button':
        track_id, track_subject, track_link = recognized_tracks.get(update.message.reply_to_message.id, (None, None, None))
        if not track_id:
            message = locales[bot_language]['messages']['unavailable']
            return await update.answer(message, show_alert=True)
        
        message = f'{track_subject}\n{track_link}'
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(locales[bot_language]['buttons']['back'], 'track_button')]])

        try:
            with FuturesSession() as session:
                response = session.get(track_link).result()
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                lyrics_div = soup.find('div', {'class': 'Text-module_text-gray-900__Qcj0F Text-module_fontFamily__cQFwR Text-post-module_size-base__o144k Text-module_fontWeightNormal__kB6Wg'})
                
                if lyrics_div:
                    message += f'\n\n{lyrics_div.get_text(strip=True)}'
                    return await callback_answer(update, message, markup)
                else:
                    message = locales[bot_language]['messages']['no_lyrics']
                    return await update.answer(message, show_alert=True)
        except RequestException:
            message = locales[bot_language]['messages']['no_lyrics']
            return await update.answer(message, show_alert=True)
    # Provide similar tracks
    elif update.data == 'track_similar_button':
        track_id, _, _ = recognized_tracks.get(update.message.reply_to_message.id, (None, None, None))
        if not track_id:
            message = locales[bot_language]['messages']['unavailable']
            return await update.answer(message, show_alert=True)

        markup = InlineKeyboardMarkup([[InlineKeyboardButton(locales[bot_language]['buttons']['back'], 'track_button')]])

        try:
            related_json = await shazam.related_tracks(track_id, limit=5)
            related_tracks = [f"{track['share']['subject']}\n{track['share']['href']}" for track in related_json.get('tracks', [])]
            message = '\n'.join(related_tracks)
            return await callback_answer(update, message, markup)
        except (KeyError, FailedDecodeJson):
            message = locales[bot_language]['messages']['unavailable']
            return await update.answer(message, show_alert=True)


@bot.on_message(filters.new_chat_members, 1)
async def new_chat(_, update: Message):
    '''Handler for new chats bot added'''
    await insert_chat(update.chat.id)