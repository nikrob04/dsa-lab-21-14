# bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties

# Токен
API_TOKEN = "8021741271:AAEzHY2cvSPp9b_ju22XkCLnr-BALjl71z8"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Бот и диспетчер
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Словарь для хранения валют
currency_data = {}
# Состояния пользователя
user_states = {}

# Меню-клавиатура
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/save_currency")],
        [KeyboardButton(text="/show_currencies")],
        [KeyboardButton(text="/convert")]
    ],
    resize_keyboard=True
)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для сохранения курсов валют.\nВыберите действие из меню ниже:",
        reply_markup=menu_kb
    )

# Команда /save_currency
@dp.message(Command("save_currency"))
async def cmd_save_currency(message: Message):
    await message.answer("Введите название валюты (например, USD):")
    user_states[message.from_user.id] = "waiting_for_currency_name"

# Команда /show_currencies
@dp.message(Command("show_currencies"))
async def cmd_show_currencies(message: Message):
    if not currency_data:
        await message.answer("Пока что нет сохранённых валют.")
    else:
        text = "<b>Сохранённые курсы валют:</b>\n"
        for currency, rate in currency_data.items():
            text += f"{currency} = {rate} RUB\n"
        await message.answer(text)

# Команда /convert
@dp.message(Command("convert"))
async def cmd_convert(message: Message):
    await message.answer("Введите название валюты, которую хотите конвертировать в рубли (например, USD):")
    user_states[message.from_user.id] = "waiting_for_convert_currency"

# Обработка сообщений (ввод названия валюты, курса, суммы)
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id

    # Сохранение курса валюты
    if user_states.get(user_id) == "waiting_for_currency_name":
        user_states[user_id] = {
            "step": "waiting_for_currency_value",
            "currency": message.text.upper().strip()
        }
        await message.answer("Введите курс к рублю (например, 94.5):")

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("step") == "waiting_for_currency_value":
        try:
            user_input = message.text.strip().replace(',', '.')
            rate = float(user_input)

            currency = user_states[user_id]["currency"]
            currency_data[currency] = rate

            await message.answer(f"Сохранено: {currency} = {rate} RUB")
            user_states.pop(user_id)

        except ValueError:
            await message.answer("Пожалуйста, введите числовое значение для курса (например, 94.5 или 94,5).")

    # Конвертация валюты
    elif user_states.get(user_id) == "waiting_for_convert_currency":
        currency = message.text.upper().strip()
        if currency not in currency_data:
            await message.answer(f"Валюта {currency} не найдена. Сначала добавьте её через /save_currency.")
        else:
            user_states[user_id] = {
                "step": "waiting_for_convert_amount",
                "currency": currency
            }
            await message.answer(f"Введите сумму в {currency}, которую хотите перевести в рубли:")

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("step") == "waiting_for_convert_amount":
        try:
            amount_str = message.text.strip().replace(',', '.')
            amount = float(amount_str)

            currency = user_states[user_id]["currency"]
            rate = currency_data[currency]
            result = round(amount * rate, 2)

            await message.answer(f"{amount} {currency} = {result} RUB")
            user_states.pop(user_id)

        except ValueError:
            await message.answer("Пожалуйста, введите корректное число (например, 10.5 или 10,5).")

    else:
        await message.answer("Выберите команду из меню или введите /start")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
