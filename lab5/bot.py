# bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
import os
import psycopg2
from aiogram import types

API_TOKEN = os.getenv("API_TOKEN")

# Токен  "8021741271:AAEzHY2cvSPp9b_ju22XkCLnr-BALjl71z8"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Бот и диспетчер
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname = "currency_bot_db",
        user = "postgres",
        password = "postgres"
    )



# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет!",
        reply_markup=menu_kb
    )


# Список администраторов
admins = ["admin_chat_id_1", "admin_chat_id_2"]  # Замените на реальный chat_id администраторов

@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: types.Message):
    # Проверяем, является ли пользователь администратором
    if str(message.chat.id) not in admins:
        await message.answer("Нет доступа к команде.")
        return
    
    # Отображаем кнопки для администраторов
    manage_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить валюту")],
            [KeyboardButton(text="Удалить валюту")],
            [KeyboardButton(text="Изменить курс валюты")]
        ],
        resize_keyboard=True
    )

    await message.answer("Выберите действие:", reply_markup=manage_kb)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
