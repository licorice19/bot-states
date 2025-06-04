from .common import *

def register_all_handlers(bot: TeleBot):
    """
    Registers all command handlers with the bot instance.
    """
    bot.register_message_handler(start_handler, commands=['start'], pass_bot=True)
    bot.register_message_handler(help_handler, commands=['help'], pass_bot=True)
    bot.register_message_handler(cancel_handler_state, commands=['cancel'], state='*', pass_bot=True)
    bot.register_message_handler(codes_handler, commands=['codes'], pass_bot=True)
    bot.register_message_handler(process_codes_input, state=CodesStates.waiting_for_codes, pass_bot=True)
    bot.register_message_handler(gen_handler, commands=['gen'], pass_bot=True)
    bot.register_message_handler(mycodes_handler, commands=['mycodes'], pass_bot=True)