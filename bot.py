import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ================== CONFIG ==================
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID = 1001788720  # твой ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

# Храним выбранный размер поля для пользователей
user_settings = {}

# ================== KEYBOARDS ==================
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("🎮 Новая игра", "⚙️ Настройки", "📜 Правила")

settings_kb = ReplyKeyboardMarkup(resize_keyboard=True)
settings_kb.add("3x3", "4x4", "5x5", "6x6").add("⬅️ Назад")

# ================== HANDLERS ==================
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_settings[message.from_user.id] = 3  # по умолчанию 3x3
    await message.answer("Привет! Я бот крестики-нолики 🎲", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "⚙️ Настройки")
async def settings_menu(message: types.Message):
    await message.answer("Выбери размер поля:", reply_markup=settings_kb)

@dp.message_handler(lambda m: m.text in ["3x3", "4x4", "5x5", "6x6"])
async def set_board_size(message: types.Message):
    size = int(message.text[0])
    user_settings[message.from_user.id] = size
    await message.answer(f"✅ Размер поля изменён на {size}x{size}", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "📜 Правила")
async def rules(message: types.Message):
    await message.answer("Чтобы победить, нужно собрать 3 одинаковых подряд "
                         "(по горизонтали, вертикали или диагонали).")

@dp.message_handler(lambda m: m.text == "🎮 Новая игра")
async def new_game(message: types.Message):
    size = user_settings.get(message.from_user.id, 3)
    board = InlineKeyboardMarkup(row_width=size)
    for i in range(size * size):
        board.insert(InlineKeyboardButton("⬜", callback_data=f"cell_{i}"))
    await message.answer(f"🎮 Новая игра {size}x{size}", reply_markup=board)

@dp.callback_query_handler(lambda c: c.data.startswith("cell_"))
async def handle_cell(callback: types.CallbackQuery):
    await callback.answer("Ход пока не работает (Этап 3 😉)")

# ================== FLASK + RENDER ==================
@app.route("/")
def home():
    return "TicTacToe Bot is running!"

def start_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    t = Thread(target=start_bot)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
