
from telebot import TeleBot, types
from ..states import CodesStates # Убедитесь, что путь к states правильный
import logging
from ..utils.barcode_utils import parse_codes_input, generate_ean13_barcode_image_bytes
import random
from .. import config
from ..entities import AppTeleBot


logger = logging.getLogger(__name__)

# Глобальный словарь user_codes. Для персистентности рассмотрите другое хранилище.
user_codes = {} 

# --- Вспомогательная функция для проверки админских прав ---
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS

# --- Существующие хендлеры (start, codes, process_codes, mycodes, gen, cancel) ---
# Модифицируем help_handler
def help_handler(message: types.Message, bot: TeleBot):
    """
    Handles the /help command.
    """
    user_id = message.from_user.id if message.from_user else None

    help_text_parts = [
        "<b>Доступные команды:</b>",
        "/start - Приветственное сообщение",
        "/help - Показать это сообщение",
        "/codes - Загрузить временный список EAN-кодов (12 или 13 цифр).",
        "  Коды разделяются пробелом, запятой или новой строкой.",
        "  Этот список будет использован командой /gen, если ей не передать код напрямую.",
        "/gen <code>[код]</code> - Сгенерировать штрих-код для указанного EAN.",
        "  Если <code>[код]</code> не указан, будет использован случайный код из временного списка.",
        "/mycodes - Показать текущий временный список кодов.",
        "/cancel - Отменить текущую операцию (например, ввод кодов)."
    ]

    if user_id and is_admin(user_id):
        help_text_parts.extend([
            "\n<b>Команды администратора:</b>",
            "/unauthorized - Показать список неавторизованных попыток доступа.",
            "/addadmin <code>[user_id]</code> - Добавить администратора.",
            "/deladmin <code>[user_id]</code> - Удалить администратора.",
            "/reloadcfg - Перезагрузить конфигурацию из файла."
        ])
    
    bot.send_message(chat_id=message.chat.id, text="\n".join(help_text_parts), parse_mode="HTML")

# ... (остальные ваши start_handler, codes_handler, и т.д. остаются как есть)
def start_handler(message: types.Message, bot: TeleBot):
    bot.send_message(
        chat_id=message.chat.id,
        text="Привет! Используйте /help для просмотра доступных команд."
    )

def codes_handler(message: types.Message, bot: TeleBot):
    if not message.from_user:
        logger.warning("Codes command received without from_user in message: %s", message.message_id)
        return
    bot.set_state(message.from_user.id, CodesStates.waiting_for_codes, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Введите список EAN-кодов (12 или 13 цифр).\n"
        "Разделители: пробел, запятая, новая строка.\n"
        "Этот список будет временным. Отмените ввод командой /cancel.",
        reply_to_message_id=message.message_id,
    )
    # Очистка предыдущих кодов пользователя при новом вызове /codes
    if message.from_user.id in user_codes:
        del user_codes[message.from_user.id]


def process_codes_input(message: types.Message, bot: TeleBot):
    if not message.from_user: return # Добавим проверку
    if message.text and message.text.startswith('/'):
        bot.delete_state(message.from_user.id, message.chat.id)
        # bot.send_message(message.chat.id, "Ввод кодов отменен, так как введена другая команда.")
        # Просто выходим, чтобы команда обработалась стандартно
        return # Важно, чтобы другая команда могла быть обработана, не отправляем сообщение здесь

    codes = parse_codes_input(message.text or "") # Учитываем, что message.text может быть None
    logger.debug(f"Parsed codes for user {message.from_user.id}: {codes}")

    if not codes:
        bot.send_message(
            message.chat.id,
            "Не удалось распознать коды. Убедитесь, что ввели их правильно (12 или 13 цифр, разделены пробелом/запятой/новой строкой).",
            reply_to_message_id=message.message_id,
        )
        # Не сбрасываем состояние, даем пользователю попробовать еще раз или отменить
        return
    
    # Сохраняем коды в словаре user_codes; для личных чатов user_id == chat_id
    user_codes[message.from_user.id] = codes

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
        message.chat.id,
        f"Коды успешно загружены ({len(codes)} шт.).\n"
        "Теперь используйте /gen для генерации штрих-кодов.",
        reply_to_message_id=message.message_id,
    )

def mycodes_handler(message: types.Message, bot: TeleBot):
    if not message.from_user:
        logger.warning("Mycodes command received without from_user in message: %s", message.message_id)
        return

    codes = user_codes.get(message.from_user.id, [])
    if codes:
        codes_text = "\n".join(codes)
        bot.send_message(
            message.chat.id,
            f"Ваш временный список EAN-кодов ({len(codes)} шт.):\n<code>{codes_text}</code>",
            reply_to_message_id=message.message_id,
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            "У вас нет временного списка EAN-кодов. Используйте /codes для загрузки.",
            reply_to_message_id=message.message_id,
        )

def gen_handler(message: types.Message, bot: TeleBot):
    if not message.from_user: return
    
    args = (message.text or "").split(maxsplit=1)
    code_to_gen = None

    if len(args) > 1:
        potential_code = args[1].strip()
        if potential_code.isdigit() and (len(potential_code) == 12 or len(potential_code) == 13):
            code_to_gen = potential_code
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, укажите корректный EAN-код (12 или 13 цифр) после команды /gen, например: <code>/gen 123456789012</code>",
                reply_to_message_id=message.message_id,
                parse_mode="HTML"
            )
            return # Выход, если аргумент неверный
    else:
        # Генерация из списка пользователя (только если это личный чат)
        if message.from_user.id == message.chat.id:
            codes = user_codes.get(message.from_user.id, [])
            if codes:
                code_to_gen = random.choice(codes)
            else:
                bot.send_message(
                    message.chat.id,
                    "Укажите EAN-код (например, <code>/gen 123456789012</code>) "
                    "или загрузите список кодов через /codes.",
                    reply_to_message_id=message.message_id,
                    parse_mode="HTML"
                )
                return
        else: # Если не в личке и код не указан
             bot.send_message(
                    message.chat.id,
                    "В групповых чатах необходимо явно указать код для генерации: <code>/gen <код></code>",
                    reply_to_message_id=message.message_id,
                    parse_mode="HTML"
                )
             return


    if code_to_gen:
        try:
            barcode_image_bytes = generate_ean13_barcode_image_bytes(code_to_gen)
            if barcode_image_bytes:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=barcode_image_bytes,
                    caption=f"Штрих-код для: <code>{code_to_gen}</code>",
                    reply_to_message_id=message.message_id,
                    parse_mode="HTML"
                )
            else: # generate_ean13_barcode_image_bytes вернул None (ошибка внутри)
                bot.send_message(
                    message.chat.id,
                    f"Не удалось сгенерировать штрих-код для <code>{code_to_gen}</code>. Проверьте корректность кода (12 или 13 цифр).",
                    reply_to_message_id=message.message_id,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Ошибка генерации штрих-кода для {code_to_gen}: {e}")
            bot.send_message(
                message.chat.id,
                f"Произошла ошибка при генерации штрих-кода для <code>{code_to_gen}</code>.",
                reply_to_message_id=message.message_id,
                parse_mode="HTML"
            )


def cancel_handler_state(message: types.Message, bot: TeleBot):
    if not message.from_user:
        logger.warning("Cancel attempt without from_user in message: %s", message.message_id)
        return 

    current_state = bot.get_state(message.from_user.id, message.chat.id)
    if current_state is None:
        bot.send_message(message.chat.id, "Нет активной операции для отмены.")
        return

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Операция отменена.")

# --- Новые административные команды ---

def unauthorized_list_handler(message: types.Message, bot: AppTeleBot):
    if not message.from_user or not is_admin(message.from_user.id):
        # Middleware должен был уже отсечь, но на всякий случай
        bot.reply_to(message, "Эта команда доступна только администраторам.")
        return

    # Получаем экземпляр middleware через атрибут бота, установленный при инициализации
    if not hasattr(bot, 'auth_middleware_instance_ref'):
        bot.reply_to(message, "Ошибка: Middleware не найден.")
        logger.error("auth_middleware_instance_ref not found on bot object for unauthorized_list_handler.")
        return
    
    auth_middleware = bot.auth_middleware_instance_ref
    if auth_middleware is None:
        logger.error("auth_middleware_instance_ref is None on bot object for unauthorized_list_handler.")
        return

    unknown_users_data = auth_middleware.unknown_users_access_attempts

    print(f"Unknown users data: {unknown_users_data}")  # Для отладки

    if not unknown_users_data:
        bot.reply_to(message, "Записей о неавторизованных попытках доступа нет.")
        return

    response_parts = ["<b>Неавторизованные попытки доступа:</b>\n"]
    for user_id_str, info in unknown_users_data.items():
        part = (
            f"\n<b>ID:</b> <code>{user_id_str}</code>\n"
            f"  Username: <code>@{info.get('username', 'N/A')}</code>\n"
            f"  Full Name: {info.get('full_name', 'N/A')}\n"
            f"  Attempts: {info.get('attempts', 1)}\n"
            f"  Chat ID: {info.get('chat_id', 'N/A')}"
        )
        response_parts.append(part)
    
    full_response = "".join(response_parts)

    # Отправка длинных сообщений по частям
    if len(full_response) > 4096:
        current_chunk = ""
        for line in full_response.splitlines(keepends=True):
            if len(current_chunk) + len(line) > 4050: # Оставляем небольшой запас
                bot.send_message(message.chat.id, current_chunk, parse_mode="HTML")
                current_chunk = line
            else:
                current_chunk += line
        if current_chunk: # Отправить остаток
            bot.send_message(message.chat.id, current_chunk, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, full_response, parse_mode="HTML")

    # Опционально: Очистить список после показа
    # auth_middleware.unknown_users_access_attempts.clear()
    # bot.send_message(message.chat.id, "<i>Список попыток доступа очищен.</i>", parse_mode="HTML")


def add_admin_handler(message: types.Message, bot: TeleBot):
    if not message.from_user or not is_admin(message.from_user.id):
        bot.reply_to(message, "Эта команда доступна только администраторам.")
        return

    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.reply_to(message, "Использование: <code>/addadmin [user_id]</code>", parse_mode="HTML")
        return

    try:
        new_admin_id = int(parts[1])
        if new_admin_id <= 0: # Простая проверка на валидность ID
            raise ValueError("User ID must be a positive integer.")
    except ValueError:
        bot.reply_to(message, "Неверный ID пользователя. ID должен быть целым положительным числом.")
        return

    if new_admin_id in config.ADMIN_IDS:
        bot.reply_to(message, f"Пользователь с ID <code>{new_admin_id}</code> уже является администратором.")
        return

    config.ADMIN_IDS.append(new_admin_id) # Обновляем список в памяти
    if config.save_config(): # Сохраняем в файл (save_config вернет True при успехе)
        bot.reply_to(message, f"Пользователь с ID <code>{new_admin_id}</code> успешно добавлен в администраторы.\n"
                              "Изменения применены и сохранены в конфигурации.")
        logger.info(f"Admin {new_admin_id} added by {message.from_user.id}. ADMIN_IDS in memory: {config.ADMIN_IDS}")
    else:
        # Пытаемся откатить изменение в памяти, если сохранение не удалось
        if new_admin_id in config.ADMIN_IDS:
            config.ADMIN_IDS.remove(new_admin_id)
        bot.reply_to(message, "Произошла ошибка при сохранении изменений в файл конфигурации. Администратор не добавлен.")


def del_admin_handler(message: types.Message, bot: TeleBot):
    if not message.from_user or not is_admin(message.from_user.id):
        bot.reply_to(message, "Эта команда доступна только администраторам.")
        return

    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.reply_to(message, "Использование: <code>/deladmin [user_id]</code>", parse_mode="HTML")
        return

    try:
        admin_id_to_remove = int(parts[1])
    except ValueError:
        bot.reply_to(message, "Неверный ID пользователя. ID должен быть числом.")
        return
    
    if admin_id_to_remove == message.from_user.id:
        bot.reply_to(message, "Вы не можете удалить самого себя из администраторов этой командой.")
        return
    
    # Проверяем, есть ли такой ID в текущем списке админов в памяти
    if admin_id_to_remove not in config.ADMIN_IDS:
        bot.reply_to(message, f"Пользователь с ID <code>{admin_id_to_remove}</code> не найден в списке администраторов.")
        return

    config.ADMIN_IDS.remove(admin_id_to_remove) # Обновляем список в памяти
    if config.save_config(): # Сохраняем в файл
        bot.reply_to(message, f"Пользователь с ID <code>{admin_id_to_remove}</code> успешно удален из администраторов.\n"
                              "Изменения применены и сохранены в конфигурации.")
        logger.info(f"Admin {admin_id_to_remove} removed by {message.from_user.id}. ADMIN_IDS in memory: {config.ADMIN_IDS}")
    else:
        # Пытаемся откатить изменение в памяти, если сохранение не удалось
        if admin_id_to_remove not in config.ADMIN_IDS: # Если его там уже нет (маловероятно, но все же)
             config.ADMIN_IDS.append(admin_id_to_remove) # Возвращаем обратно
        bot.reply_to(message, "Произошла ошибка при сохранении изменений в файл конфигурации. Администратор не удален.")

def reload_config_handler(message: types.Message, bot: TeleBot):
    if not message.from_user or not is_admin(message.from_user.id):
        bot.reply_to(message, "Эта команда доступна только администраторам.")
        return
    
    try:
        config.load_config() # Вызываем функцию перезагрузки из модуля config
        # Обновляем уровень логгера для основного логгера приложения (если он настраивался глобально)
        # и для логгера текущего модуля
        logging.getLogger().setLevel(config.LOG_LEVEL)
        logger.setLevel(config.LOG_LEVEL)

        bot.reply_to(message, "Конфигурация успешно перезагружена из файла. "
                              "Уровень логирования обновлен.")
        logger.info(f"Config reloaded by admin {message.from_user.id}. New ADMIN_IDS: {config.ADMIN_IDS}, LOG_LEVEL: {config.LOG_LEVEL}")
    except Exception as e:
        logger.error(f"Ошибка при перезагрузке конфигурации: {e}", exc_info=True)
        bot.reply_to(message, f"Произошла ошибка при перезагрузке конфигурации: {e}")