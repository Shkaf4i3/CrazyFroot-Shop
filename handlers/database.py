from os import getenv
from dotenv import load_dotenv
from psqlpy import ConnectionPool, SingleQueryResult, QueryResult
from psqlpy.extra_types import BigInt

from aiogram.types import CallbackQuery


load_dotenv()
db_pool = ConnectionPool(password=getenv('password'),
                         db_name=getenv('dbname'),
                         username=getenv('user'),
                         host=getenv('host'),
                         port=5432,
                         max_db_pool_size=10)


# Создание базы данных с таблицами Social Club, Epic Games и Users
async def create_table() -> None:
    cursor = await db_pool.connection()

    await cursor.execute(querystring='''CREATE TABLE IF NOT EXISTS Social_Club (
                        login TEXT NOT NULL,
                        password TEXT NOT NULL)''')

    await cursor.execute(querystring='''CREATE TABLE IF NOT EXISTS Epic_Games (
                        login TEXT NOT NULL,
                        password TEXT NOT NULL)''')

    await cursor.execute(querystring='''CREATE TABLE IF NOT EXISTS Users (
                        id BIGINT PRIMARY KEY,
                        first_name VARCHAR(255),
                        balance INTEGER DEFAULT 0)''')


# Вывод информации о балансе пользователя
async def get_count_balance(first_name):
    cursor = await db_pool.connection()

    data: SingleQueryResult = await cursor.execute(
                            querystring='SELECT balance FROM Users WHERE first_name = ($1)',
                            parameters=[first_name])

    result = data.result()
    return result[0]['balance']

# Добавление пользователя в базу данных
async def add_user(user_id: int, first_name: str):
    connection = await db_pool.connection()
    cursor = connection.transaction()

    await cursor.begin()

    data = await cursor.fetch(
                querystring='SELECT * FROM Users WHERE first_name = ($1)',
                parameters=[first_name],
            )

    if not data.result():
        await cursor.execute(
            querystring='INSERT INTO Users (id, first_name) VALUES ($1, $2)',
            parameters=[BigInt(user_id), first_name],
        )
        await cursor.commit()


# Добавление товаров в БД
async def get_sc(login: str, password: str):
    connection = await db_pool.connection()
    cursor = connection.transaction()

    await cursor.begin()

    data = await cursor.fetch(
                querystring='SELECT * FROM Social_Club WHERE login = ($1) AND password = ($2)',
                parameters=[login, password])

    if data.result():
            return False
    else:
        await cursor.execute(
            querystring='INSERT INTO Social_Club VALUES ($1, $2)',
            parameters=[login, password])
        await cursor.commit()
        return True

async def get_eg(login: str, password: str):
    connection = await db_pool.connection()
    cursor = connection.transaction()

    await cursor.begin()

    data = await cursor.fetch(
                querystring='SELECT * FROM Epic_Games WHERE login = ($1) AND password = ($2)',
                parameters=[login, password])

    if data.result():
            return False
    else:
        await cursor.execute(
            querystring='INSERT INTO Epic_Games VALUES ($1, $2)',
            parameters=[login, password])
        await cursor.commit()
        return True


# Поиск товаров в таблицах Social Club и Epic Games
async def get_count_sc():
    cursor = await db_pool.connection()

    data: SingleQueryResult = await cursor.execute(querystring='SELECT COUNT(*) FROM Social_Club')

    result = data.result()
    return result[0]['count']

async def get_count_eg():
    cursor = await db_pool.connection()

    data: SingleQueryResult = await cursor.execute(querystring='SELECT COUNT(*) FROM Epic_Games')

    result = data.result()
    return result[0]['count']


# Список пользователей из БД
async def get_list_user():
    cursor = await db_pool.connection()

    data: QueryResult = await cursor.execute(querystring='SELECT * FROM Users')

    result = data.result()
    user_list = "\n".join([f"{user['id']} | {user['first_name']} | {user['balance']}" for user in result])

    return user_list


# Выдача товаров из бд
async def get_item_sc(callback: CallbackQuery):
    cursor = await db_pool.connection()
    data: QueryResult = await cursor.fetch(
        querystring='SELECT login, password FROM Social_Club LIMIT 1'
        )
    result = data.result()

    if result:
        log = result[0]['login']
        pas = result[0]['password']

        await callback.answer()
        await callback.message.answer(f'Твои данные: {log}:{pas}')
        await cursor.execute(
                'DELETE FROM Social_Club WHERE login = ($1) AND password = ($2)',
                (log, pas))
    else:
        await callback.answer()
        await callback.message.answer('В данный момент товаров нет 😰')

async def get_item_eg(callback: CallbackQuery):
    cursor = await db_pool.connection()
    data: QueryResult = await cursor.fetch(
        querystring='SELECT login, password FROM Epic_Games LIMIT 1'
        )
    result = data.result()

    if result:
        log = result[0]['login']
        pas = result[0]['password']

        await callback.answer()
        await callback.message.answer(f'Твои данные: {log}:{pas}')
        await cursor.execute(
                'DELETE FROM Epic_Games WHERE login = ($1) AND password = ($2)',
                (log, pas))
    else:
        await callback.answer()
        await callback.message.answer('В данный момент товаров нет 😰')
