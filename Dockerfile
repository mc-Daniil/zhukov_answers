FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Копируем код
COPY ./src /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir aiogram

# Запускаем бота
CMD ["python", "bot.py"]
