from .common import *

def register_all_handlers(bot: TeleBot):
    """
    Registers all command handlers with the bot instance.
    """
    bot.register_message_handler(start_handler, commands=['start'], pass_bot=True, )
    bot.register_message_handler(help_handler, commands=['help'], pass_bot=True)
    bot.register_message_handler(cancel_handler_state, commands=['cancel'], state='*', pass_bot=True)
    bot.register_message_handler(codes_handler, commands=['codes'], pass_bot=True)
    bot.register_message_handler(process_codes_input, state=CodesStates.waiting_for_codes, pass_bot=True)
    bot.register_message_handler(gen_handler, commands=['gen'], pass_bot=True)
    bot.register_message_handler(mycodes_handler, commands=['mycodes'], pass_bot=True)
    bot.register_message_handler(unauthorized_list_handler, commands=['unauthorized'], pass_bot=True)
    bot.register_message_handler(add_admin_handler, commands=['addadmin'], pass_bot=True)
    bot.register_message_handler(del_admin_handler, commands=['deladmin'], pass_bot=True)
    bot.register_message_handler(reload_config_handler, commands=['reloadcfg'], pass_bot=True)