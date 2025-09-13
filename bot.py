import os
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# === Твой токен ===
TOKEN = "8461263670:AAHNklJHXKbnz94WUpau1TH1CVfMy1saW6o"
WEBHOOK_URL = "https://tic-tac-toe-3q20.onrender.com/webhook"

# === Инициализация бота ===
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)


# === Хендлер /start ===
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎮 Новая игра"))
    kb.add(KeyboardButton("⚙️ Настройки"))
    kb.add(KeyboardButton("📜 Правила"))

    await message.answer(
        "Привет! Это бот 🎲\n\nВыбери действие в меню:",
        reply_markup=kb
    )


# === Хендлер на кнопки ===
@dp.message_handler(lambda msg: msg.text == "📜 Правила")
async def rules_cmd(message: types.Message):
    await message.answer("Чтобы победить, нужно собрать 3 в ряд (по горизонтали, вертикали или диагонали).")


# === Flask endpoint для webhook ===
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = types.Update(**request.json)
    await dp.process_update(update)
    return "ok", 200


@app.route("/")
def index():
    return "Bot is running!"


# === Устанавливаем webhook при старте ===
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == "__main__":
    asyncio.run(on_startup())
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
