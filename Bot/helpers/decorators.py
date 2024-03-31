from typing import Callable, Union  # Importing necessary types for type hints

from cachetools import TTLCache  # Importing TTLCache from cachetools for caching with TTL
from functools import wraps  # Importing wraps from functools for function decorators

from pyrogram import Client  # Importing the Client class from pyrogram
from pyrogram.types import CallbackQuery, Message  # Importing necessary types from pyrogram

from Bot import loop, locales  # Importing necessary variables from the Bot module
from Bot.logging import logger  # Importing the logger function from the Bot.logging module
from Bot.database.database import get_user_language  # Importing the get_user_language function from the Bot.database.database module
from Bot.helpers.ratelimiter import RateLimiter  # Importing the RateLimiter class from the Bot.helpers.ratelimiter module

rate_limiter = RateLimiter()  # Initializing the RateLimiter instance
warned_users = TTLCache(maxsize=128, ttl=60)  # Initializing TTLCache for warned users


def run_rate_limiter(func: Callable) -> Callable:
    '''Decorator to limit the rate of function calls.'''
    @wraps(func)
    async def decorator(client: Client, update: Union[Message, CallbackQuery]):
        '''Inner function handling rate limiting.'''
        user_id = update.from_user.id
        user_name = update.from_user.username
        user_language = update.from_user.language_code
        bot_language = await get_user_language(user_id, user_language, 'bot_language')

        # Check if the user has reached the rate limit
        if await rate_limiter.acquire(user_id):
            # Send a warning message if it's the first time the user is warned
            if user_id not in warned_users:
                message = locales[bot_language]['messages']['limit']
                response_method = update.reply_text if isinstance(update, Message) else update.answer
                await response_method(message, True)
                warned_users[user_id] = 1
                logger('Bot').info(f'{user_name}({user_id}) has reached request limit...')
            return

        return await func(client, update)

    return decorator


def run_sync_in_thread(func: Callable) -> Callable:
    '''Decorator to run a synchronous function in a separate thread.'''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        '''Inner function wrapping the synchronous function.'''
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper