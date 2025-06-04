from telebot import TeleBot, types

def start_handler(message: types.Message, bot: TeleBot):
    """
    Handles the /start command.
    """
    bot.send_message(
        chat_id=message.chat.id,
        text="Welcome! Use /help to see available commands."
    )

def help_handler(message: types.Message, bot: TeleBot):
    """
    Handles the /help command.
    """
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/test_state - Test Handler"
    )
    bot.send_message(chat_id=message.chat.id, text=help_text)

def test_state_handler(message: types.Message, bot: TeleBot):
    """
    Handles the /test_state command.
    """
    bot.send_message(
        chat_id=message.chat.id,
        text="This is a test state handler."
    )