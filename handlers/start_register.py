from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import keyboards
from create_bot import bot, dp
from models.db import create_user, is_user_registered, get_work_status_by_user_id, update_work_status
from states import RegisterUserState
from utils.section_mapper import section_mapping

async def toggle_work_status(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    is_work = get_work_status_by_user_id(user_id)
    new_status = not is_work  # Инвертировать текущий статус
    update_work_status(user_id, new_status)  # Обновить статус в базе данных

    if new_status:
        await bot.send_message(message.from_user.id,'Ваш статус "На работе"\n'
                            'уведомления включены')
    else:
        await bot.send_message(message.from_user.id,'Ваш статус "Дома"\n'
                            'уведомления отключены')
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f'Здравствуй, @{message.from_user.username}!\n'
                                            f'Для регистрации нажмите на кнопку /register')

async def register_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if is_user_registered(user_id):
        # Создание клавиатуры для ответа
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Да", callback_data="add_more_sections"))
        markup.add(InlineKeyboardButton("Нет", callback_data="no_more_sections"))

        await message.reply('Вы уже зарегистрированы. Хотите добавить ещё секции?', reply_markup=markup)
    else:
        await RegisterUserState.waiting_for_section.set()
        await bot.send_message(message.chat.id, "Выберите секции (можно выбрать несколько) затем нажмите на команду ниже\n💾---- /save ----💾", reply_markup=keyboards.markup_register)

@dp.callback_query_handler(lambda c: c.data == 'add_more_sections')
async def add_more_sections(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await RegisterUserState.waiting_for_section.set()
    await bot.send_message(callback_query.from_user.id, "Выберите дополнительные секции затем нажмите на команду ниже\n💾---- /save ----💾:", reply_markup=keyboards.markup_register)

@dp.callback_query_handler(lambda c: c.data == 'no_more_sections')
async def no_more_sections(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Дополнительные секции не добавлены.")
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=None)

async def handle_section_choice(callback: types.CallbackQuery, state: FSMContext):
    section_code = callback.data
    user_data = await state.get_data()
    selected_sections = user_data.get("selected_sections", [])
    selected_sections.append(section_code)
    await state.update_data(selected_sections=selected_sections)

    await callback.answer("Секция добавлена. Выберите еще секции или завершите регистрацию, нажав на команду \n/save выше ☝️", show_alert=True)

async def finish_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_section_codes = user_data.get("selected_sections", [])

    # Проверка, что хотя бы одна секция была выбрана
    if not selected_section_codes:
        await message.reply("Пожалуйста, выберите хотя бы одну секцию. или нажмите \"Отмена\"",reply_markup=keyboards.markup)
        return

    selected_section_names = [section_mapping.get(code, "Неизвестная секция") for code in selected_section_codes]

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    is_work = True

    create_user(user_id, first_name, selected_section_names, is_work)
    await state.finish()


    if len(selected_section_names) == 1:
        await message.reply(f"Вы выбрали секцию: {selected_section_names[0]}. Регистрация успешно завершена!",reply_markup=types.ReplyKeyboardRemove())

    else:
        await message.reply(f"Вы выбрали секции: {', '.join(selected_section_names)}. Регистрация успешно завершена!",reply_markup=types.ReplyKeyboardRemove())

async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()  # Завершаем текущее состояние
    await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())


def register_handlers_client(dp):
    dp.register_message_handler(cancel_action,lambda message: message.text and message.text.lower() == "отмена", state="*")
    dp.register_message_handler(start, commands=['start'], state=None)
    dp.register_message_handler(register_command, commands=['register'], state=None)
    dp.register_callback_query_handler(handle_section_choice, state=RegisterUserState.waiting_for_section)
    dp.register_message_handler(finish_registration, commands=['save'], state=RegisterUserState.waiting_for_section)
    dp.register_message_handler(toggle_work_status, commands=['change_status'], state=None)

