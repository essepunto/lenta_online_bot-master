from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterUserState(StatesGroup):
    waiting_for_section = State()
    finishing_registration = State()