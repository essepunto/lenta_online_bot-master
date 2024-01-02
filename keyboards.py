from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, KeyboardButton

# Создаем клавиатуру
markup_register = types.InlineKeyboardMarkup(row_width=2)

# Определяем список кнопок
buttons = [
    types.InlineKeyboardButton(text="Бакалея", callback_data="section_bak"),
    types.InlineKeyboardButton(text="Напитки", callback_data="section_nap"),
    types.InlineKeyboardButton(text="Кондитерск. изделия", callback_data="section_ki"),
    types.InlineKeyboardButton(text="Бытовая химия", callback_data="section_bh"),
    types.InlineKeyboardButton(text="Гастроном 1", callback_data="section_g1"),
    types.InlineKeyboardButton(text="Гастроном 2", callback_data="section_g2"),
    types.InlineKeyboardButton(text="Домашний интерьер", callback_data="section_di"),
    types.InlineKeyboardButton(text="Кулинар Произ-во", callback_data="section_kp"),
    types.InlineKeyboardButton(text="МультиМедиа-РабОтдых", callback_data="section_mmrio"),
    types.InlineKeyboardButton(text="Мясное Произ-во", callback_data="section_mp"),
    types.InlineKeyboardButton(text="Овощи и Фрукты", callback_data="section_sof"),
    types.InlineKeyboardButton(text="Одежда и Обувь", callback_data="section_oio"),
    types.InlineKeyboardButton(text="Пекарня", callback_data="section_pek")
]

# Добавляем кнопки в клавиатуру
markup_register.add(*buttons)

# Отдельная клавиатура для завершения регистрации
markup_finish_registration = InlineKeyboardMarkup()
finish_button = InlineKeyboardButton("Завершить регистрацию", callback_data="finish_registration")
markup_finish_registration.add(finish_button)



markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_button = KeyboardButton("Отмена")
markup.add(cancel_button)
