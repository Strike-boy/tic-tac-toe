import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)

# Берём токен из переменных окружения
TOKEN = os.getenv("TG_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Хранилище активных игр
games = {}

# Клавиатура главного меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🎮 Новая игра"))
main_kb.add(KeyboardButton("⚙️ Настройки"))
main_kb.add(KeyboardButton("📜 Правила"))

# /start
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет! Я бот ✖️⭕ Крестики-Нолики.\n\nВыбери действие:",
        reply_markup=main_kb
    )

# Правила
@dp.message_handler(lambda m: m.text == "📜 Правила")
async def rules_cmd(message: types.Message):
    await message.answer(
        "Правила простые:\n\n"
        "1. Игроки ходят по очереди.\n"
        "2. Побеждает тот, кто соберёт ряд из 3 символов (по горизонтали, вертикали или диагонали).\n"
        "3. Если поле заполнено и нет победителя — ничья."
    )

# Настройки (пока только заглушка)
@dp.message_handler(lambda m: m.text == "⚙️ Настройки")
async def settings_cmd(message: types.Message):
    await message.answer("В будущих версиях тут можно будет выбрать размер поля (3x3, 4x4, ...).")

# Новая игра
@dp.message_handler(lambda m: m.text == "🎮 Новая игра")
async def new_game_cmd(message: types.Message):
    user_id = message.from_user.id
    games[user_id] = [" "] * 9
    await send_board(message.chat.id, user_id)

# Отрисовка поля
async def send_board(chat_id, user_id):
    board = games[user_id]
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, 9, 3):
        kb.row(
            KeyboardButton(board[i] if board[i] != " " else str(i+1)),
            KeyboardButton(board[i+1] if board[i+1] != " " else str(i+2)),
            KeyboardButton(board[i+2] if board[i+2] != " " else str(i+3))
        )
    await bot.send_message(chat_id, "Твой ход! Выбери клетку:", reply_markup=kb)

# Ходы игрока
@dp.message_handler(lambda m: m.text.isdigit() and int(m.text) in range(1, 10))
async def player_move(message: types.Message):
    user_id = message.from_user.id
    if user_id not in games:
        await message.answer("Сначала начни новую игру 🎮")
        return

    pos = int(message.text) - 1
    board = games[user_id]

    if board[pos] != " ":
        await message.answer("Клетка занята! Выбери другую.")
        return

    # Ход игрока (X)
    board[pos] = "X"

    if check_winner(board, "X"):
        await message.answer("Поздравляю, ты выиграл! 🎉", reply_markup=main_kb)
        del games[user_id]
        return
    if " " not in board:
        await message.answer("Ничья 🤝", reply_markup=main_kb)
        del games[user_id]
        return

    # Ход бота (O)
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            break

    if check_winner(board, "O"):
        await message.answer("Ты проиграл 😢", reply_markup=main_kb)
        del games[user_id]
        return
    if " " not in board:
        await message.answer("Ничья 🤝", reply_markup=main_kb)
        del games[user_id]
        return

    games[user_id] = board
    await send_board(message.chat.id, user_id)

# Проверка победителя
def check_winner(board, symbol):
    wins = [
        [0,1,2],[3,4,5],[6,7,8], # линии
        [0,3,6],[1,4,7],[2,5,8], # колонки
        [0,4,8],[2,4,6]          # диагонали
    ]
    return any(all(board[i] == symbol for i in line) for line in wins)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)