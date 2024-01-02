from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import models.db
from models.db import get_user_info, get_section_by_user_id


# Функция для создания inline клавиатуры с информацией о профиле
def create_profile_keyboard(user_info, sections):
    keyboard = InlineKeyboardMarkup(row_width=2)

    # Добавляем кнопку для каждой секции
    for section in sections:
        keyboard.add(InlineKeyboardButton(text=section, callback_data=f"section_info_{section}"))

    # Дополнительные кнопки, если нужно
    keyboard.add(InlineKeyboardButton(text="Подробнее о статусе", callback_data="status_info"))

    return keyboard

# Обработчик команды /profile
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    sections = get_section_by_user_id(user_id)

    # Формирование сообщения профиля
    profile_message = f"👤 Профиль: {user_info['name']}\n" \
                      f"📌 Статус: {user_info['status']}"

    keyboard = create_profile_keyboard(user_info, sections)
    await message.answer(profile_message, reply_markup=keyboard)

# Обработчики callback данных
async def handle_section_info(callback_query: types.CallbackQuery):
    section = callback_query.data[len("section_info_"):]
    # Обработка информации о секции
    await callback_query.message.answer(f"Информация о секции {section}")

async def handle_status_info(callback_query: types.CallbackQuery):
    # Обработка информации о статусе
    status = models.db.get_work_status_by_user_id(callback_query.from_user.id)
    await callback_query.message.answer(f"Информация о вашем \n{status}")

# Регистрация обработчиков
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_profile, commands=['profile'])
    dp.register_callback_query_handler(handle_section_info, lambda c: c.data.startswith("section_info_"))
    dp.register_callback_query_handler(handle_status_info, lambda c: c.data == "status_info")
