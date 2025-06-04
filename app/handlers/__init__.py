from .common import *


def register_all_handlers(bot: TeleBot):
    """
    Registers all command handlers with the bot instance.
    """
    bot.register_message_handler(start_handler, commands=['start'], pass_bot=True)
    bot.register_message_handler(help_handler, commands=['help'], pass_bot=True)
    bot.register_message_handler(test_state_handler, commands=['test_state'], pass_bot=True)