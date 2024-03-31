from sqlite3 import connect  # Importing connect from sqlite3 module for synchronous database connection
from aiosqlite import connect as connect_async, IntegrityError as aiosqlite_IntegrityError  # Importing connect from aiosqlite for asynchronous database connection


async def execute_query(query, *args):
    '''Asynchronous function to execute a query'''
    async with connect_async('Database/database.sqlite3') as database:
        async with database.cursor() as cursor:
            await cursor.execute(query, args)
            await database.commit()


def create_database():
    '''Function to create database and tables'''
    with connect('Database/database.sqlite3') as database:
        cursor = database.cursor()
        # Creating users table if not exists
        cursor.execute('CREATE TABLE IF NOT EXISTS users(user_id INTEGER UNIQUE PRIMARY KEY, user_name TEXT, bot_language TEXT, speech_language TEXT, user_option INTEGER)')
        # Creating chats table if not exists
        cursor.execute('CREATE TABLE IF NOT EXISTS chats(chat_id INTEGER UNIQUE PRIMARY KEY)')
        database.commit()


async def insert_data(query, *args):
    '''Asynchronous function to insert data into the database'''
    try:
        await execute_query(query, *args)
    except aiosqlite_IntegrityError:
        pass


async def insert_user(user_id, user_name, bot_language, speech_language, user_option):
    '''Asynchronous function to insert user data into the database'''
    query = 'INSERT INTO users VALUES (?, ?, ?, ?, ?)'
    await insert_data(query, user_id, user_name, bot_language, speech_language, user_option)
    update_query = 'UPDATE users SET user_name = ?, bot_language = ?, speech_language = ?, user_option = ? WHERE user_id = ?'
    await insert_data(update_query, user_name, bot_language, speech_language, user_option, user_id)


async def insert_chat(chat_id):
    '''Asynchronous function to insert chat data into the database'''
    query = 'INSERT INTO chats VALUES (?)'
    await insert_data(query, chat_id)


async def get_data(query, *args):
    '''Asynchronous function to retrieve data from the database'''
    async with connect_async('Database/database.sqlite3') as database:
        async with database.cursor() as cursor:
            await cursor.execute(query, args)
            data = await cursor.fetchone()
            return data[0] if data else None


async def get_user_option(user_id):
    '''Asynchronous function to get user option from the database'''
    query = 'SELECT user_option FROM users WHERE user_id = ?'
    return await get_data(query, user_id)


async def get_user_language(user_id, default_language, column):
    '''Asynchronous function to get user language from the database'''
    query = f'SELECT {column} FROM users WHERE user_id = ?'
    return await get_data(query, user_id) or default_language