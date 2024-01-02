import csv
import os
import subprocess
import sys

import sqlalchemy
from aiogram import types, Dispatcher
from sqlalchemy.orm import sessionmaker

from create_bot import bot
from models.db import SkuToSection, engine

# Создаем сессию для подключения к базе данных
Session = sessionmaker(bind=engine)

async def process_csv_file(file_path, message: types.Message):
    with Session() as session:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                try:
                    sku, section_name = row
                    record = SkuToSection(sku=sku, section_name=section_name)
                    session.add(record)
                    session.commit()
                except sqlalchemy.exc.IntegrityError:
                    session.rollback()
                    await message.reply(f"Ошибка: элемент с SKU  уже существует.")
                    return

async def upload_csv(message: types.Message):
    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    file_path = "temp.csv"
    with open(file_path, "wb") as new_file:
        new_file.write(downloaded_file.getvalue())

    await process_csv_file(file_path, message)
    os.remove(file_path)
    await message.reply("CSV файл обработан.")

async def run_script(message: types.Message):
    subprocess.run([sys.executable, "db_init.py"])
    await message.reply("Скрипт выполнен.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(upload_csv, content_types=['document'])
    dp.register_message_handler(run_script, commands=['postgres_init'])

