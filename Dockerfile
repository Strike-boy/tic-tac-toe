# Базовый образ Python
FROM python:3.10-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Запуск
CMD ["python", "bot.py"]
