import logging
import os
from threading import Thread

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

API_TOKEN = os.getenv("API_TOKEN")  # берём токен из Render переменных окружения

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Flask app для Render
app = Flask(__name__)

# Храним настройки пользователей
user_settings = {}

# --- Кнопки меню ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("🎮 Новая игра", "⚙️ Настройки")
main_menu.add("📜 Правила")

# --- Функция построения пустого поля ---
def build_board(size):
    board = InlineKeyboardMarkup(row_width=size)
    for r in range(size):
        row = []
        for c in range(size):
            row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{r}_{c}"))
        board.row(*row)
    return board

# --- Команда старт ---
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_settings[message.from_user.id] = 3  # по умолчанию 3x3
    await message.answer("Добро пожаловать в игру ❌⭕!\nВыбери действие ниже 👇", reply_markup=main_menu)

# --- Новая игра ---
@dp.message_handler(lambda message: message.text == "🎮 Новая игра")
async def new_game(message: types.Message):
    size = user_settings.get(message.from_user.id, 3)
    await message.answer(f"Новая игра {size}×{size}!\nЧтобы победить, нужно собрать 3 в ряд.", reply_markup=build_board(size))

# --- Настройки ---
@dp.message_handler(lambda message: message.text == "⚙️ Настройки")
async def settings(message: types.Message):
    kb = InlineKeyboardMarkup()
    for s in [3, 4, 5, 6]:
        kb.add(InlineKeyboardButton(f"{s}×{s}", callback_data=f"set_size_{s}"))
    await message.answer("Выбери размер поля:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("set_size_"))
async def set_size(callback: types.CallbackQuery):
    size = int(callback.data.split("_")[2])
    user_settings[callback.from_user.id] = size
    await callback.answer(f"Размер поля изменён на {size}×{size}")
    await callback.message.edit_text(f"✅ Размер поля установлен: {size}×{size}")

# --- Правила ---
@dp.message_handler(lambda message: message.text == "📜 Правила")
async def rules(message: types.Message):
    await message.answer("Правила игры:\n\nЧтобы победить, нужно собрать 3 одинаковых символа ❌ или ⭕ подряд — по горизонтали, вертикали или диагонали.\nУдачи!")

# --- Пустые клики по полю ---
@dp.callback_query_handler(lambda c: c.data.startswith("cell_"))
async def cell_click(callback: types.CallbackQuery):
    await callback.answer("Ходы будут доступны позже 😉")

# --- Фоновый запуск бота ---
def start_bot():
    executor.start_polling(dp, skip_updates=True)

# --- Flask route для Render ---
@app.route("/")
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    t = Thread(target=start_bot)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

