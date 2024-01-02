from dotenv import load_dotenv
import os

load_dotenv()

# Загрузка переменных окружения
API_TOKEN = os.getenv('API_TOKEN')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Формирование строки подключения к базе данных
PG_DSN = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
