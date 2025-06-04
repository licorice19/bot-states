from telebot.handler_backends import State, StatesGroup

class CodesStates(StatesGroup):
    waiting_for_codes = State()