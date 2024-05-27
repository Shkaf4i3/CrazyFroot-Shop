import psycopg
from os import getenv
from dotenv import load_dotenv

from aiogram.types import CallbackQuery


load_dotenv()
conninfo = f''' host={getenv('host')}
                port={getenv('port')}
                dbname={getenv('dbname')}
                user={getenv('user')}
                password={getenv('password')}
            '''


# Создание базы данных с таблицами Social Club, Epic Games и Users
# async def create_table():
#     async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
#         async with aconn.cursor() as cursor:
#             await cursor.execute('''CREATE TABLE IF NOT EXISTS Social_Club (
#                         login TEXT NOT NULL,
#                         password TEXT NOT NULL)''')
#             await aconn.commit()

#             await cursor.execute('''CREATE TABLE IF NOT EXISTS Epic_Games (
#                         login TEXT NOT NULL,
#                         password TEXT NOT NULL)''')
#             await aconn.commit()

#             await cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
#                         first_name VARCHAR(255),
#                         balance INT)''')
#             await aconn.commit()


# Вывод информации о балансе пользователя
async def get_count_balance(first_name):
    table_name = 'Users'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
            async with aconn.cursor() as cursor:
                await cursor.execute('SELECT balance FROM %s WHERE first_name = (%%s)' % table_name,
                               [first_name])
                total_count = await cursor.fetchone()
    return total_count[0]


# Добавление пользователя в базу данных
async def add_user(first_name):
    default_balance = 0
    table_name = 'Users'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:
            await cursor.execute(
                'SELECT * FROM %s WHERE first_name = %%s' % table_name,
                [first_name]
            )
            if not await cursor.fetchone():
                await cursor.execute(
                    'INSERT INTO %s (first_name, balance) VALUES (%%s, %%s)' % table_name,
                    [first_name, default_balance]
                )
                await aconn.commit()


# Добавление товаров в БД
async def get_sc(login, password):
    table_name = 'Social_Club'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:

            await cursor.execute(
                'SELECT * FROM %s WHERE login = (%%s) AND password = (%%s)' % table_name,
                [login, password])
            result = await cursor.fetchone()

            if result:
                return False
            else:
                await cursor.execute(
                    'INSERT INTO %s VALUES (%%s, %%s)' % table_name,
                    [login, password])
                await aconn.commit()
                return True

async def get_eg(login, password):
    table_name = 'Epic_Games'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:

            await cursor.execute(
                'SELECT * FROM %s WHERE login = (%%s) AND password = (%%s)' % table_name,
                [login, password])
            result = await cursor.fetchone()

            if result:
                return False
            else:
                await cursor.execute(
                    'INSERT INTO %s VALUES (%%s, %%s)' % table_name,
                    [login, password])
                await aconn.commit()
                return True


# Поиск товаров в таблицах Social Club и Epic Games
async def get_count_sc():
    table_name = 'Social_Club'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:
            await cursor.execute('SELECT COUNT(*) FROM %s' % table_name)
            total_count = await cursor.fetchone()
    return total_count[0]

async def get_count_eg():
    table_name = 'Epic_Games'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:
            await cursor.execute('SELECT COUNT(*) FROM %s' % table_name)
            total_count = await cursor.fetchone()
    return total_count[0]


# Список пользователей из БД
async def get_list_user():
    table_name = 'Users'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:
            await cursor.execute('SELECT * FROM %s' % table_name)
            total_count = await cursor.fetchall()
            user_list = "\n".join([f"{user[0]} | {user[1]}" for user in total_count])
        return user_list


# Выдача товаров из бд
async def get_item_sc(callback: CallbackQuery):
    table_name = 'Social_Club'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:
            await cursor.execute('SELECT login, password FROM %s LIMIT 1' % table_name)
            data = await cursor.fetchone()

            if data:
                login, password = data
                await callback.answer()
                await callback.message.answer(f'Твои данные: {login}:{password}')
                await cursor.execute(
                    'DELETE FROM %s WHERE login = %s AND password = %s' % (table_name, '%s', '%s'),
                    (login, password))
                await aconn.commit()
            else:
                await callback.answer()
                await callback.message.answer('В данный момент товаров нет 😰')


async def get_item_eg(callback: CallbackQuery):
    table_name = 'Epic_Games'
    async with await psycopg.AsyncConnection.connect(conninfo=conninfo) as aconn:
        async with aconn.cursor() as cursor:
            await cursor.execute('SELECT login, password FROM %s LIMIT 1' % table_name)
            data = await cursor.fetchone()

            if data:
                login, password = data
                await callback.answer()
                await callback.message.answer(f'Твои данные: {login}:{password}')
                await cursor.execute(
                    'DELETE FROM %s WHERE login = %s AND password = %s' % (table_name, '%s', '%s'),
                    (login, password))
                await aconn.commit()
            else:
                await callback.answer()
                await callback.message.answer('В данный момент товаров нет 😰')
