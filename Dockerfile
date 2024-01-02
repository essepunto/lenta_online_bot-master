FROM python:3.11-slim

# Установка зависимостей для psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Установите рабочую директорию в контейнере
WORKDIR /usr/src/app

# Копируйте файлы в контейнер
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запустите бота
CMD ["python", "./bot.py"]
