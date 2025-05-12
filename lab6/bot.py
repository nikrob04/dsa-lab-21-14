import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
import aiohttp

API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Клавиатуры ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/get_currencies"),
               KeyboardButton(text="/convert"),
               KeyboardButton(text="/manage_currency")]],
    resize_keyboard=True
)

manage_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Добавить валюту"),
               KeyboardButton(text="Удалить валюту"),
               KeyboardButton(text="Изменить курс валюты")]],
    resize_keyboard=True
)

# --- Состояния пользователя и список админов ---
user_states = {}
admins = []

# --- Загрузка админов из микросервиса ---
async def load_admins():
    global admins
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5003/admins") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    admins = data.get("admins", [])
                    print(f"[i] Админы загружены: {admins}")
                else:
                    print("[!] Не удалось получить список админов")
    except Exception as e:
        print(f"[!] Ошибка при загрузке админов: {e}")

# --- Команды ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_kb)

@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message):
    if str(message.from_user.id) not in admins:
        await message.answer("У вас нет доступа к этой функции.")
        return
    await message.answer("Выберите действие:", reply_markup=manage_kb)

@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5002/currencies") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not data:
                        await message.answer("Список валют пуст.")
                        return
                    text = "<b>Список валют:</b>\n"
                    for item in data:
                        text += f"🔹 {item['currency_name']}: {item['rate']:.3f} RUB\n"
                    await message.answer(text)
                else:
                    await message.answer("Ошибка при получении валют.")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

@dp.message(Command("convert"))
async def cmd_convert(message: Message):
    await message.answer("Введите название валюты:")
    user_states[message.from_user.id] = "waiting_for_currency_to_convert"

# --- Обработка всего остального ---
@dp.message()
async def handle_all(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "Добавить валюту":
        if str(user_id) not in admins:
            await message.answer("У вас нет доступа к этой функции.")
            return
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_name"
        return

    elif text == "Удалить валюту":
        if str(user_id) not in admins:
            await message.answer("У вас нет доступа к этой функции.")
            return
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_to_delete"
        return

    elif text == "Изменить курс валюты":
        if str(user_id) not in admins:
            await message.answer("У вас нет доступа к этой функции.")
            return
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_to_edit"
        return

    elif user_states.get(user_id) == "waiting_for_currency_name":
        user_states[user_id] = {"action": "add_currency", "currency": text.upper()}
        await message.answer("Введите курс к рублю:")
        return

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "add_currency":
        try:
            rate = float(text.replace(",", "."))
            currency = user_states[user_id]["currency"]
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:5001/load", json={"currency_name": currency, "rate": rate}) as resp:
                    if resp.status == 200:
                        await message.answer(f"Валюта {currency} успешно добавлена.", reply_markup=main_kb)
                    elif resp.status == 409:
                        await message.answer("Данная валюта уже существует.", reply_markup=main_kb)
                    else:
                        await message.answer("Ошибка при добавлении валюты.", reply_markup=main_kb)
        except ValueError:
            await message.answer("Введите корректное число.")
        finally:
            user_states.pop(user_id)
        return

    elif user_states.get(user_id) == "waiting_for_currency_to_delete":
        currency = text.upper()
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:5001/delete", json={"currency_name": currency}) as resp:
                if resp.status == 200:
                    await message.answer(f"Валюта {currency} удалена.", reply_markup=main_kb)
                elif resp.status == 404:
                    await message.answer("Такая валюта не найдена.", reply_markup=main_kb)
                else:
                    await message.answer("Ошибка при удалении валюты.", reply_markup=main_kb)
        user_states.pop(user_id)
        return

    elif user_states.get(user_id) == "waiting_for_currency_to_edit":
        user_states[user_id] = {"action": "edit_currency", "currency": text.upper()}
        await message.answer("Введите новый курс:")
        return

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "edit_currency":
        try:
            rate = float(text.replace(",", "."))
            currency = user_states[user_id]["currency"]
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:5001/update_currency", json={"currency_name": currency, "rate": rate}) as resp:
                    if resp.status == 200:
                        await message.answer(f"Курс валюты {currency} обновлён.", reply_markup=main_kb)
                    elif resp.status == 404:
                        await message.answer("Такая валюта не найдена.", reply_markup=main_kb)
                    else:
                        await message.answer("Ошибка при обновлении курса.", reply_markup=main_kb)
        except ValueError:
            await message.answer("Введите корректное число.")
        finally:
            user_states.pop(user_id)
        return

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "convert":
        try:
            amount = float(text.replace(",", "."))
            currency = user_states[user_id]["currency"]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:5002/convert?currency_name={currency}&amount={amount}") as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        rub = result["converted_to_rub"]
                        await message.answer(f"{amount:.3f} {currency} = {rub:.3f} RUB", reply_markup=main_kb)
                    elif resp.status == 404:
                        await message.answer("Такая валюта не найдена.", reply_markup=main_kb)
                    else:
                        await message.answer("Ошибка при конвертации.", reply_markup=main_kb)
        except ValueError:
            await message.answer("Введите корректное число.")
        finally:
            user_states.pop(user_id)
        return

    elif user_states.get(user_id) == "waiting_for_currency_to_convert":
        user_states[user_id] = {"action": "convert", "currency": text.upper()}
        await message.answer("Введите сумму для конвертации:")
        return

    else:
        await message.answer("Я вас не понял. Выберите команду из меню.", reply_markup=main_kb)

# --- Запуск бота ---
async def main():
    await load_admins()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
