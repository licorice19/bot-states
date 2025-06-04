from telebot import TeleBot, types
from ..states import CodesStates
import logging
from ..utils.barcode_utils import parse_codes_input, generate_ean13_barcode_image_bytes
import random

logger = logging.getLogger(__name__)

user_codes = {}

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
        "/start - Приветственное сообщение\n"
        "/help - Показать это сообщение\n"
        "/codes - загрузить временный список EAN-кодов (12 или 13 цифр).\n"
        "Коды разделяются пробелом, запятой или новой строкой. Этот список будет использован командой /gen, если ей не передать код напрямую.\n"
        "/gen [код] - сгенерировать штрих-код для указанного EAN. "
        "Если [код] не указан, будет использован случайный код из временного списка (загруженного через /codes).\n"
        "/mycodes - показать текущий временный список кодов.\n"
    )
    bot.send_message(chat_id=message.chat.id, text=help_text)


def codes_handler(message: types.Message, bot: TeleBot):
    """
    Обрабатывает команду /codes для загрузки временного списка EAN-кодов.
    """
    if not message.from_user:  # Проверка на наличие from_user
        logger.warning("Codes command received without from_user in message: %s", message.message_id)
        return

    bot.set_state(message.from_user.id, CodesStates.waiting_for_codes, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Введите список EAN-кодов (12 или 13 цифр).\n"
        "Разделители: пробел, запятая, новая строка.\n"
        "Этот список будет временным для текущей сессии или до следующей команды /codes. Отмените ввод, введя другую команду или /cancel.",
        reply_to_message_id=message.message_id,
    )
    with bot.retrieve_data(message.from_user.id, message.chat.id) as session_data: # type: ignore[misc]
        if 'user_codes' in session_data and session_data.get('user_codes', {}) is not None:
            del session_data['user_codes']

def process_codes_input(message: types.Message, bot: TeleBot):
    """Обработчик для сообщений, когда администратор в состоянии UserStates.awaiting_codes."""

    if message.text and message.text.startswith('/'):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, "Ввод кодов отменен, так как введена другая команда.")
        return
    
    codes = parse_codes_input(message.text)
    print(f"Parsed codes: {codes}")  # Для отладки, можно удалить позже

    if not codes:
        bot.send_message(
            message.chat.id,
            "Не удалось распознать коды. Пожалуйста, убедитесь, что вы ввели их в правильном формате (12 или 13 цифр).",
            reply_to_message_id=message.message_id,
        )
        return
    
    if message.from_user.id == message.chat.id:
        user_codes[message.from_user.id] = codes  # Сохраняем коды в сессии

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
        message.chat.id,
        f"Коды успешно загружены:\n"
        "Теперь вы можете использовать команду /gen для генерации штрих-кодов.",
        reply_to_message_id=message.message_id,
    )

def mycodes_handler(message: types.Message, bot: TeleBot):
    """
    Обрабатывает команду /mycodes для отображения текущего временного списка EAN-кодов.
    """
    if not message.from_user:  # Проверка на наличие from_user
        logger.warning("Mycodes command received without from_user in message: %s", message.message_id)
        return


    codes = user_codes.get(message.from_user.id, [])
    if codes:
        codes_text = "\n".join(codes)
        bot.send_message(
            message.chat.id,
            f"Ваш временный список EAN-кодов:\n{codes_text}",
            reply_to_message_id=message.message_id,
        )
    else:
        bot.send_message(
            message.chat.id,
            "У вас нет временного списка EAN-кодов. Используйте команду /codes для его загрузки.",
            reply_to_message_id=message.message_id,
        )

def gen_handler(message: types.Message, bot: TeleBot):
    """ Обрабатывает команду /gen для генерации штрих-кода EAN-13."""
    args = message.text.split(maxsplit=1)
    code_to_gen = None

    if len(args) > 1:
        potential_code = args[1].strip()
        if potential_code.isdigit() and (len(potential_code) == 12 or len(potential_code) == 13):
            code_to_gen = potential_code
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, укажите корректный EAN-код (12 или 13 цифр) после команды /gen.",
                reply_to_message_id=message.message_id,
            )
    else:
        if message.from_user.id == message.chat.id:
            codes = user_codes.get(message.from_user.id, [])
            if codes:
                selected_code = random.choice(codes)
                code_to_gen = selected_code
            else:
                bot.send_message(
                    message.chat.id,
                    "Для генерации укажите EAN-код после команды (например, /gen 123456789012) "
                    "или сначала загрузите временный список кодов с помощью команды /codes.",
                    reply_to_message_id=message.message_id,
                )
                return
    if code_to_gen:
        barcode_image_bytes = generate_ean13_barcode_image_bytes(code_to_gen)
        if barcode_image_bytes:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=barcode_image_bytes,
                caption=f"Штрих-код для: {code_to_gen}",
                reply_to_message_id=message.message_id,
            )
        else:
            bot.send_message(
                message.chat.id,
                f"Не удалось сгенерировать штрих-код для кода: {code_to_gen}. "
                "Пожалуйста, убедитесь, что код корректен (12 или 13 цифр).",
                reply_to_message_id=message.message_id,
            )



def cancel_handler_state(message: types.Message, bot: TeleBot):

    """
    Отменяет текущую операцию (работает в любом состоянии).
    """
    if not message.from_user: # Проверка
        logger.warning("Cancel attempt without from_user in message: %s", message.message_id)
        return 

    current_state = bot.get_state(message.from_user.id, message.chat.id)
    if current_state is None:
        bot.send_message(message.chat.id, "Нет активной операции для отмены.")
        return

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Операция отменена.")