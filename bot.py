from aiogram import executor

from create_bot import dp
from handlers import notifier, start_register
from models import get_csv

get_csv.register_handlers(dp)
notifier.register_handlers(dp)
start_register.register_handlers_client(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

