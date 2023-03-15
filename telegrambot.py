import psycopg2

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = 'ага так и дал ключ'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Подключение к базе данных
conn = psycopg2.connect(
    host="127.0.0.1",
    database="codeforce",
    user="postgres",
    password="root"
)

cur = conn.cursor()

# Выполнение запроса

@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply("/find_one это поиск по одному атрибуту\n/find  это просто поиск 1 и более атрибутов\n /search_by_name поиск по имени \n/search_by_number поиск по номеру")


@dp.message_handler(commands=['find_one'])
async def cmd_one(message: types.Message):
    if len(message.text.split()) == 1:
        await message.reply("Выбери тему и уровень сложности задачи. Например: /find_one реализация 900")
        return

    # Получение названия темы и уровня сложности из сообщения пользователя
    topic, hard = message.text.split()[1:]

    b = f'{{{topic}}}'
    cur.execute("SELECT * FROM code WHERE data_temp ~ %s AND difficulty = %s",
                (b, hard))
    rows = cur.fetchall()
    for i in rows[:11]:
        await message.reply(i)


@dp.message_handler(commands=['find'])
async def cmd_find(message: types.Message):
    if len(message.text.split()) == 1:
        await message.reply("Выбери тему и уровень сложности задачи. Например: /find математика реализация 900")
        return

    # Получение названия темы и уровня сложности из сообщения пользователя
    topic, level, hard = message.text.split()[1:]

    b = f'{{.*{topic}.*{level}.*}}'
    cur.execute("SELECT * FROM code WHERE data_temp ~ %s AND difficulty = %s",
                (b, hard))
    rows = cur.fetchall()
    for i in rows[:11]:
        await message.reply(i)


@dp.message_handler(commands=['search_by_number'])
async def cmd_num(message: types.Message):
    if len(message.text.split()) == 1:
        await message.reply("Выбери тему и уровень сложности задачи. Например: /search_by_number 1351B")
        return
    topic = message.text.split()[1:]

    cur.execute("SELECT * FROM code WHERE name ~ %s",
                (topic))
    rows = cur.fetchall()
    for i in rows[:11]:
        await message.reply(i)

@dp.message_handler(commands=['search_by_name'])
async def cmd_name(message: types.Message):
    if len(message.text.split()) == 1:
        await message.reply("Выбери тему и уровень сложности задачи. Например: /search_by_name Квадрат")
        return
    topic = message.text.split()[1:]

    cur.execute("SELECT * FROM code WHERE category_task ~ %s",
                (topic))
    rows = cur.fetchall()
    for i in rows[:11]:
        await message.reply(i)

# Закрытие курсора и соединения с базой данных
cur.close()
conn.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)