# Файл: config.py
import configparser
import os
import logging # Добавим логгирование и сюда

logger = logging.getLogger(__name__)

# --- Константы для конфигурации ---
CONFIG_FILE_NAME = '../config.ini'
CONFIG_SECTION_NAME = 'Settings'

# --- Путь к файлу конфигурации ---
# Предполагается, что config.py и config.ini находятся в одной директории
# или config.ini находится в корне проекта, а config.py в поддиректории.
# Этот путь должен быть корректным относительно места запуска скрипта или абсолютным.
# Для простоты, если config.py в корне пакета, а config.ini рядом:
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)


# --- Значения по умолчанию ---
DEFAULT_TOKEN = "YOUR_DEFAULT_TOKEN_IF_NOT_IN_CONFIG"
DEFAULT_ADMIN_IDS_LIST = [] # Пустой список по умолчанию
DEFAULT_LOG_LEVEL = "DEBUG"

# --- Инициализация переменных конфигурации значениями по умолчанию ---
TOKEN = DEFAULT_TOKEN
ADMIN_IDS = list(DEFAULT_ADMIN_IDS_LIST) # Используем list() для создания копии
LOG_LEVEL = DEFAULT_LOG_LEVEL

def load_config(file_path: str = CONFIG_FILE_PATH):
    """
    Загружает конфигурацию из INI-файла в глобальные переменные этого модуля.
    """
    global TOKEN, ADMIN_IDS, LOG_LEVEL

    # Сначала установим значения по умолчанию
    TOKEN = DEFAULT_TOKEN
    ADMIN_IDS[:] = DEFAULT_ADMIN_IDS_LIST # Очищаем и заполняем существующий список
    LOG_LEVEL = DEFAULT_LOG_LEVEL
    
    config_parser = configparser.ConfigParser()

    if os.path.exists(file_path):
        try:
            config_parser.read(file_path, encoding='utf-8') # Добавим encoding

            if config_parser.has_section(CONFIG_SECTION_NAME):
                TOKEN = config_parser.get(CONFIG_SECTION_NAME, 'TOKEN', fallback=DEFAULT_TOKEN)
                
                admin_ids_str = config_parser.get(CONFIG_SECTION_NAME, 'ADMIN_IDS', fallback='')
                if admin_ids_str and admin_ids_str.strip():
                    try:
                        ADMIN_IDS[:] = [int(admin_id.strip()) for admin_id in admin_ids_str.split(',') if admin_id.strip()]
                    except ValueError:
                        logger.warning(
                            f"Неверный формат ADMIN_IDS в '{file_path}'. "
                            f"Используется значение по умолчанию: {DEFAULT_ADMIN_IDS_LIST}"
                        )
                        ADMIN_IDS[:] = DEFAULT_ADMIN_IDS_LIST
                else:
                    ADMIN_IDS[:] = DEFAULT_ADMIN_IDS_LIST

                LOG_LEVEL = config_parser.get(CONFIG_SECTION_NAME, 'LOG_LEVEL', fallback=DEFAULT_LOG_LEVEL).upper()
            else:
                logger.info(f"Секция '[{CONFIG_SECTION_NAME}]' не найдена в '{file_path}'. Используются значения по умолчанию.")
        except configparser.Error as e:
            logger.error(f"Ошибка парсинга файла конфигурации '{file_path}': {e}. Используются значения по умолчанию.")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при загрузке конфигурации '{file_path}': {e}. Используются значения по умолчанию.")
    else:
        logger.warning(f"Файл конфигурации '{file_path}' не найден. Используются значения по умолчанию. "
                       "Пожалуйста, создайте файл config.ini или укажите правильный путь.")

    logger.info(f"Конфигурация загружена: ADMIN_IDS={ADMIN_IDS}, LOG_LEVEL={LOG_LEVEL}")


def save_config(file_path: str = CONFIG_FILE_PATH):
    """
    Сохраняет текущие значения TOKEN, ADMIN_IDS, LOG_LEVEL в INI-файл.
    """
    config_parser = configparser.ConfigParser()
    
    if not config_parser.has_section(CONFIG_SECTION_NAME):
        config_parser.add_section(CONFIG_SECTION_NAME)
        
    config_parser.set(CONFIG_SECTION_NAME, 'TOKEN', str(TOKEN)) # Убедимся, что токен это строка
    admin_ids_str = ",".join(map(str, ADMIN_IDS))
    config_parser.set(CONFIG_SECTION_NAME, 'ADMIN_IDS', admin_ids_str)
    config_parser.set(CONFIG_SECTION_NAME, 'LOG_LEVEL', str(LOG_LEVEL))

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            config_parser.write(f)
        logger.info(f"Конфигурация успешно сохранена в '{file_path}'.")
        return True
    except IOError as e:
        logger.error(f"Не удалось записать в файл конфигурации '{file_path}': {e}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при сохранении конфигурации '{file_path}': {e}")
        return False

load_config()