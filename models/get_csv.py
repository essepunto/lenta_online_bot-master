import csv
import os
import subprocess
import sys

import sqlalchemy
from aiogram import types, Dispatcher
from sqlalchemy.orm import Session, sessionmaker

from create_bot import bot
from models.db import SkuToSection, engine

Session = sessionmaker(bind=engine)

async def process_csv_file(file_path):
    with Session() as session:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            try:
                for row in reader:
                    sku, section_name = row
                    record = SkuToSection(sku=sku, section_name=section_name)
                    session.add(record)

                    session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                session.rollback()  # Откатываем изменения, если произошла ошибка
                # Здесь вы можете добавить логику обработки ошибки, например, отправить сообщение пользователю
                print("Ошибка: элемент с таким ключом уже существует.")


async def upload_csv(message: types.Message):
    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    file_path = "temp.csv"
    with open(file_path, "wb") as new_file:
        new_file.write(downloaded_file.getvalue())

    await process_csv_file(file_path)

    os.remove(file_path)  # Удаление временного файла

    await message.reply("CSV файл обработан и данные добавлены в базу данных.")


async def run_script(message: types.Message):
    # Вызов скрипта
    subprocess.run([sys.executable, "db_init.py"])
    await message.reply("Скрипт выполнен.")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(upload_csv, content_types=['document'])
    dp.register_message_handler(run_script, commands=['postgres_init'])
