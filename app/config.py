import configparser
import os # os все еще может быть полезен для определения пути к файлу конфигурации

# --- Константы для конфигурации ---
CONFIG_FILE_NAME = '../config.ini' # Имя вашего файла конфигурации
CONFIG_SECTION_NAME = 'Settings' # Имя секции в INI-файле

# --- Значения по умолчанию (если файл или опция не найдены) ---
DEFAULT_TOKEN = "default_token_from_code"
DEFAULT_ADMIN_IDS_LIST = [] # Пустой список по умолчанию
DEFAULT_LOG_LEVEL = "DEBUG"

# --- Инициализация переменных конфигурации значениями по умолчанию ---
TOKEN = DEFAULT_TOKEN
ADMIN_IDS = DEFAULT_ADMIN_IDS_LIST
LOG_LEVEL = DEFAULT_LOG_LEVEL

# --- Чтение конфигурации из файла ---
config = configparser.ConfigParser()

script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, CONFIG_FILE_NAME)

if os.path.exists(config_file_path):
    try:
        config.read(config_file_path)

        if config.has_section(CONFIG_SECTION_NAME):
            TOKEN = config.get(CONFIG_SECTION_NAME, 'TOKEN', fallback=DEFAULT_TOKEN)

            admin_ids_str = config.get(CONFIG_SECTION_NAME, 'ADMIN_IDS', fallback='') # Пустая строка как fallback
            if admin_ids_str and admin_ids_str.strip():
                try:
                    ADMIN_IDS = [int(admin_id.strip()) for admin_id in admin_ids_str.split(',') if admin_id.strip()]
                except ValueError:
                    print(f"ПРЕДУПРЕЖДЕНИЕ: Неверный формат ADMIN_IDS в '{config_file_path}'. Используется значение по умолчанию: {DEFAULT_ADMIN_IDS_LIST}")
                    ADMIN_IDS = DEFAULT_ADMIN_IDS_LIST # Возврат к значению по умолчанию при ошибке
            else:
                ADMIN_IDS = DEFAULT_ADMIN_IDS_LIST

            # Получаем LOG_LEVEL
            LOG_LEVEL = config.get(CONFIG_SECTION_NAME, 'LOG_LEVEL', fallback=DEFAULT_LOG_LEVEL)
        else:
            print(f"ИНФОРМАЦИЯ: Секция '[{CONFIG_SECTION_NAME}]' не найдена в '{config_file_path}'. Используются значения по умолчанию.")

    except configparser.Error as e:
        print(f"ОШИБКА: При парсинге файла конфигурации '{config_file_path}': {e}. Используются значения по умолчанию.")
else:
    print(f"ИНФОРМАЦИЯ: Файл конфигурации '{config_file_path}' не найден. Используются значения по умолчанию.")


print(f"Загруженная конфигурация:")
print(f"TOKEN: {TOKEN}")
print(f"ADMIN_IDS: {ADMIN_IDS} (тип: {type(ADMIN_IDS)})")
print(f"LOG_LEVEL: {LOG_LEVEL}")