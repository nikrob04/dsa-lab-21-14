import asyncio
import logging
import psycopg2
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



# Получаем токен из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")


#admins = ["851591473"]



# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Функция для подключения к базе данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="currency_bot_db",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# список chat_id админов
#admins = ["851591471"]

admins = []

def load_admins():
    global admins
    conn = get_db_connection()
    if conn is None:
        print("[!] Не удалось загрузить админов из базы.")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM admins")
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    # Записываем chat_id как строки
    admins = [str(row[0]) for row in result]
    print(f"[i] Загружено {len(admins)} админов из базы.")


# Клавиатура для администраторов
admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="/start"),
        KeyboardButton(text="/manage_currency"),
        KeyboardButton(text="/get_currencies"),
        KeyboardButton(text="/convert")
    ]],
    resize_keyboard=True
)

# Клавиатура для обычных пользователей
user_main_kb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="/start"),
        KeyboardButton(text="/get_currencies"),
        KeyboardButton(text="/convert")
    ]],
    resize_keyboard=True
)


# Клавиатура с действиями для управления валютой
manage_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить валюту"),
            KeyboardButton(text="Удалить валюту"),
            KeyboardButton(text="Изменить курс валюты")
        ]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if str(message.from_user.id) in admins:
        await message.answer("Вы администратор. Используйте меню ниже:", reply_markup=admin_main_kb)
    else:
        await message.answer("Добро пожаловать! Используйте меню ниже:", reply_markup=user_main_kb)




# Команда /manage_currency
@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message):
    if str(message.from_user.id) not in admins:
        await message.answer("Нет доступа к команде.")
        return

    await message.answer("Выберите действие:", reply_markup=manage_kb)

# Словарь для хранения текущего состояния пользователей
user_states = {}

@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message):
    conn = get_db_connection()
    if conn is None:
        await message.answer("Не удалось подключиться к базе данных.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
    currencies = cursor.fetchall()
    cursor.close()
    conn.close()

    if not currencies:
        await message.answer("В базе данных пока нет сохранённых валют.")
    else:
        text = "<b>Список валют и их курсов к рублю:</b>\n"
        for name, rate in currencies:
            text += f"🔹 {name}: {rate:.3f} RUB\n"
        await message.answer(text)


@dp.message(Command("convert"))
async def cmd_convert(message: Message):
    await message.answer("Введите название валюты:")
    user_states[message.from_user.id] = "waiting_for_currency_to_convert"


@dp.message()
async def handle_all_messages(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Если пользователь только что нажал кнопку
    if text == "Добавить валюту":
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_name"

    elif text == "Удалить валюту":
        await message.answer("Введите название валюты для удаления:")
        user_states[user_id] = "waiting_for_currency_to_delete"

    elif text == "Изменить курс валюты":
        await message.answer("Введите название валюты для изменения курса:")
        user_states[user_id] = "waiting_for_currency_to_edit"

    # --- Работа со введёнными данными ---
    elif user_states.get(user_id) == "waiting_for_currency_name":
        currency_name = text.upper()
        conn = get_db_connection()
        if conn is None:
            await message.answer("Не удалось подключиться к базе данных.")
            return
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing:
            await message.answer("Такая валюта уже существует!")
            user_states.pop(user_id)
        else:
            user_states[user_id] = {"action": "add_currency", "currency_name": currency_name}
            await message.answer("Введите курс валюты к рублю (например, 94.5):")

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "add_currency":
        try:
            rate = round(float(text.replace(",", ".")), 3)
            if rate <= 0:
                await message.answer("Курс должен быть положительным числом!")
                return
            currency_name = user_states[user_id]["currency_name"]

            conn = get_db_connection()
            if conn is None:
                await message.answer("Не удалось подключиться к базе данных.")
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
                (currency_name, rate)
            )
            conn.commit()
            cursor.close()
            conn.close()

            await message.answer(f"Валюта {currency_name} успешно добавлена с курсом {rate} RUB.")
            user_states.pop(user_id)
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число для курса!")

    elif user_states.get(user_id) == "waiting_for_currency_to_delete":
        currency_name = text.upper()
        conn = get_db_connection()
        if conn is None:
            await message.answer("Не удалось подключиться к базе данных.")
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()

        if deleted:
            await message.answer(f"Валюта {currency_name} успешно удалена.")
        else:
            await message.answer("Такой валюты нет в базе.")
        user_states.pop(user_id)

    elif user_states.get(user_id) == "waiting_for_currency_to_edit":
        currency_name = text.upper()
        conn = get_db_connection()
        if conn is None:
            await message.answer("Не удалось подключиться к базе данных.")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing:
            user_states[user_id] = {"action": "edit_currency", "currency_name": currency_name}
            await message.answer("Введите новый курс валюты:")
        else:
            await message.answer("Такой валюты нет в базе данных.")
            user_states.pop(user_id)

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "edit_currency":
        try:
            new_rate = round(float(text.replace(",", ".")), 3)
            if new_rate <= 0:
                await message.answer("Курс должен быть положительным числом!")
                return
            currency_name = user_states[user_id]["currency_name"]

            conn = get_db_connection()
            if conn is None:
                await message.answer("Не удалось подключиться к базе данных.")
                return
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE currencies SET rate = %s WHERE currency_name = %s",
                (new_rate, currency_name)
            )
            conn.commit()
            cursor.close()
            conn.close()

            await message.answer(f"Курс валюты {currency_name} успешно изменён на {new_rate} RUB.")
            user_states.pop(user_id)
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число для нового курса!")

    elif user_states.get(user_id) == "waiting_for_currency_to_convert":
        currency_name = text.upper()
        conn = get_db_connection()
        if conn is None:
            await message.answer("Не удалось подключиться к базе данных.")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            rate = result[0]
            user_states[user_id] = {"action": "convert", "currency": currency_name, "rate": rate}
            await message.answer("Введите сумму для конвертации:")
        else:
            await message.answer("Такая валюта не найдена.")
            user_states.pop(user_id)

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "convert":
        try:
            amount = float(text.replace(",", "."))
            if amount <= 0:
                await message.answer("Сумма должна быть положительной.")
                return

            currency = user_states[user_id]["currency"]
            rate = float(user_states[user_id]["rate"])
            result = round(amount * rate, 3)

            await message.answer(f"{amount:.3f} {currency} = {result:.3f} RUB")
            user_states.pop(user_id)
        except ValueError:
            await message.answer("Введите корректное число.")

    # Если команда или сообщение не распознано
    else:
        await message.answer("Я вас не понял. Выберите действие через /manage_currency или напишите команду.")


# Запуск бота
async def main():
    load_admins()  # 👈 Загружаем админов перед запуском
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())