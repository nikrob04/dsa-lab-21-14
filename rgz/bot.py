import asyncio
import logging
import psycopg2
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import aiohttp


class AddOperation(StatesGroup):
    choosing_type = State()
    entering_sum = State()
    entering_date = State()


class Register(StatesGroup):
    waiting_for_login = State()

class ViewOperations(StatesGroup):
    waiting_for_currency = State()

class DeleteUser(StatesGroup):
    waiting_for_chat_id = State()

# Получаем токен из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

operation_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ДОХОД"), KeyboardButton(text="РАСХОД")]
    ],
    resize_keyboard=True
)
currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="RUB"), KeyboardButton(text="USD"), KeyboardButton(text="EUR")]
    ],
    resize_keyboard=True
)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключение к базе данных
def get_db_connection():
    return psycopg2.connect(
        dbname="finance_bot_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот запущен! Здесь будет учёт ваших финансов.")

@dp.message(Command("reg"))
async def cmd_register(message: Message, state: FSMContext):
    conn = get_db_connection()
    cursor = conn.cursor()

    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("Вы уже зарегистрированы.")
    else:
        await message.answer("Введите логин:")
        await state.set_state(Register.waiting_for_login)

    cursor.close()
    conn.close()

@dp.message(Register.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    chat_id = message.chat.id

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (chat_id, name, is_admin) VALUES (%s, %s, %s)",
        (chat_id, login, False)
    )
    conn.commit()
    cursor.close()
    conn.close()

    await state.clear()
    await message.answer(f"Вы успешно зарегистрированы как {login}!")


@dp.message(Command("add_operation"))
async def add_operation_start(message: Message, state: FSMContext):
    chat_id = message.chat.id

    # Проверка, зарегистрирован ли пользователь
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        await message.answer("Вы не зарегистрированы. Используйте /reg.")
        return

    await state.set_state(AddOperation.choosing_type)
    await message.answer("Выберите тип операции:", reply_markup=operation_type_kb)

@dp.message(AddOperation.choosing_type)
async def process_type(message: Message, state: FSMContext):
    if message.text not in ["ДОХОД", "РАСХОД"]:
        await message.answer("Пожалуйста, выберите: ДОХОД или РАСХОД.")
        return

    await state.update_data(type=message.text)
    await state.set_state(AddOperation.entering_sum)
    await message.answer("Введите сумму операции в рублях:", reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True))


@dp.message(AddOperation.entering_sum)
async def process_sum(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректную сумму в рублях.")
        return

    await state.update_data(sum=amount)
    await state.set_state(AddOperation.entering_date)
    await message.answer("Введите дату операции в формате ГГГГ-ММ-ДД (например, 2024-03-01):")

@dp.message(AddOperation.entering_date)
async def process_date(message: Message, state: FSMContext):
    user_input = message.text.strip()

    # Возможные форматы даты
    possible_formats = ["%d-%m-%Y", "%d.%m.%Y", "%d-%m-%y", "%d.%m.%y"]

    for fmt in possible_formats:
        try:
            parsed_date = datetime.strptime(user_input, fmt).date()
            break
        except ValueError:
            continue
    else:
        await message.answer("Неверный формат даты. Используйте дд-мм-гггг, дд.мм.гггг, дд-мм-гг или дд.мм.гг")
        return

    data = await state.get_data()

    # Сохраняем операцию в базу
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
        (parsed_date, data['sum'], message.chat.id, data['type'])
    )
    conn.commit()
    cursor.close()
    conn.close()

    await state.clear()
    await message.answer("Операция успешно добавлена ✅")

@dp.message(Command("operations"))
async def cmd_operations(message: Message, state: FSMContext):
    chat_id = message.chat.id

    # Проверка регистрации
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        await message.answer("Вы не зарегистрированы. Используйте /reg.")
        return

    await state.set_state(ViewOperations.waiting_for_currency)
    await message.answer("Выберите валюту для отображения операций:", reply_markup=currency_kb)

@dp.message(ViewOperations.waiting_for_currency)
async def process_currency_choice(message: Message, state: FSMContext):
    currency = message.text.upper()
    if currency not in ["RUB", "USD", "EUR"]:
        await message.answer("Выберите одну из предложенных валют: RUB, USD или EUR.")
        return

    chat_id = message.chat.id
    rate = 1.0  # по умолчанию RUB

    # если нужно — запрашиваем курс у внешнего сервиса
    if currency in ["USD", "EUR"]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://127.0.0.1:8000/rate?currency={currency}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        rate = float(data["rate"])
                    elif resp.status == 400:
                        await message.answer("Неизвестная валюта (UNKNOWN CURRENCY).")
                        await state.clear()
                        return
                    else:
                        await message.answer("Ошибка при получении курса (500).")
                        await state.clear()
                        return
        except Exception as e:
            await message.answer(f"Ошибка подключения к внешнему сервису: {e}")
            await state.clear()
            return
            
    # получаем все операции пользователя
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, sum, type_operation FROM operations WHERE chat_id = %s ORDER BY date DESC",
        (chat_id,)
    )
    operations = cursor.fetchall()
    cursor.close()
    conn.close()

    if not operations:
        await message.answer("У вас пока нет операций.")
        await state.clear()
        return

    # формируем список
    response = f"<b>Ваши операции в {currency}:</b>\n"
    for date, amount, op_type in operations:
        converted = round(float(amount) / rate, 2)
        response += f"📅 {date} | 💰 {converted:.2f} {currency} | 📌 {op_type}\n"

    await state.clear()
    await message.answer(response, reply_markup=None)

@dp.message(Command("adeluser"))
async def cmd_deluser(message: Message, state: FSMContext):
    chat_id = message.chat.id

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        await message.answer("Вы не зарегистрированы.")
        return

    if not user[0]:
        await message.answer("У вас нет прав администратора.")
        return

    await state.set_state(DeleteUser.waiting_for_chat_id)
    await message.answer("Введите идентификатор (chat_id) пользователя, которого нужно удалить:")

@dp.message(DeleteUser.waiting_for_chat_id)
async def process_deluser(message: Message, state: FSMContext):
    target_chat_id = message.text.strip()

    if not target_chat_id.isdigit():
        await message.answer("Идентификатор должен быть числом.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (target_chat_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer("Пользователь с таким chat_id не найден.")
        cursor.close()
        conn.close()
        await state.clear()
        return

    # Удаляем операции и самого пользователя
    cursor.execute("DELETE FROM operations WHERE chat_id = %s", (target_chat_id,))
    cursor.execute("DELETE FROM users WHERE chat_id = %s", (target_chat_id,))
    conn.commit()
    cursor.close()
    conn.close()

    await message.answer(f"Пользователь с chat_id {target_chat_id} и все его операции были удалены ✅")
    await state.clear()


# Точка входа
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
