import re

from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import BotBlocked

import config
from create_bot import bot, dp
from models import db


# Функция для извлечения информации о товаре из текста
def extract_product_info(text):
    match = re.search(
        r'SKU:\s*(\d+)\s*Остатки:\s*(\d+)\s*(?:кг|шт).*?Наименование:\s*(.*?)\s*Номер секции:\s*(\d+)\s*Секция:\s*(.*?)\s*Время окончания сборки:\s*([а-яА-ЯёЁa-zA-Z0-9\s:]+)',
        text, re.DOTALL)
    if match:
        return {
            "sku": match.group(1),
            "quantity": match.group(2),
            "name": match.group(3).strip(),
            "section_number": match.group(4),
            "section": match.group(5).strip(),

        }
    else:
        return {
            "sku": None,
            "quantity": None,
            "name": None,
            "section_number": None,
            "section": None,

        }


# Функция обработки сообщения с информацией о товаре
async def process_sku_message(text, chat_id, message_id):
    product_info = extract_product_info(text)
    if not product_info["sku"]:
        print("SKU товара не найден в сообщении.")
        return

    if not product_info["section"]:
        print("Секция товара не найдена в сообщении.")
        return

    await notify_users_about_product(product_info, chat_id, message_id)


async def notify_users_about_product(product_info, chat_id, message_id):
    section = product_info["section"]
    user_ids = db.get_user_ids_by_section(section)
    for user_id in user_ids:
        await send_product_info_to_user(user_id, product_info, chat_id, message_id)


async def send_product_info_to_user(user_id, product_info, chat_id, message_id):
    try:
        is_work = db.get_work_status_by_user_id(user_id)
        if is_work:
            await send_sku_message(user_id, product_info, chat_id, message_id)
    except BotBlocked:
        print(f"Не удалось отправить сообщение пользователю {user_id}, так как бот заблокирован.")
    except Exception as e:
        print(f"Произошла ошибка при отправке сообщения пользователю {user_id}: {e}")


async def send_sku_message(user_id, product_info, chat_id, message_id):
    name = product_info["name"]
    section = product_info["section"]
    chat_id_str = str(chat_id)[4:]
    link = f"https://t.me/c/{chat_id_str}/{message_id}"

    link_button = InlineKeyboardButton(text="Перейти к сообщению 💬", url=link)
    keyboard = InlineKeyboardMarkup().add(link_button)

    message_text = (
        f"📊 Секция: {section}\n"
        f"🛒 Товар: {name}\n"
    )

    await bot.send_message(user_id, message_text, reply_markup=keyboard)


# Хэндлер для обработки сообщений с фото
async def handle_photo_message(message: types.Message):
    if message.caption:
        chat_id = message.chat.id
        message_id = message.message_id
        caption = message.caption
        async with dp.current_state(chat=message.chat.id).proxy():
            await process_sku_message(caption, chat_id, message_id)
            print(chat_id)


async def user_left(message: types.Message):
    user_id = message.left_chat_member.id
    username = message.left_chat_member.username
    db.remove_user_by_id(user_id)
    await message.answer(f"Пользователь @{username} покинул чат и был удален из базы данных.")


# Функция регистрации хэндлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_photo_message, content_types=['photo'])
    dp.register_message_handler(user_left, content_types=['left_chat_member'])
