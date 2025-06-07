# Файл: bot_logging.py
import logging
import sys

# Флаг, чтобы гарантировать, что основная настройка выполняется только один раз.
# Последующие вызовы setup_app_logging могут обновлять уровни.
_logging_configured_globally = False

def setup_app_logging(log_level_str: str, log_file: str = "app.log", force_reconfigure: bool = False):
    """
    Настраивает или перенастраивает корневой логгер приложения.

    :param log_level_str: Уровень логирования в виде строки (например, "INFO", "DEBUG").
    :param log_file: Имя файла для логирования.
    :param force_reconfigure: Если True, удаляет существующие обработчики и настраивает заново.
                              Используется, например, при перезагрузке конфига, чтобы применить новые пути к файлам или форматы.
                              Если False и логирование уже настроено, только обновит уровни.
    """
    global _logging_configured_globally

    # Преобразуем строковый уровень в числовой logging уровень
    numeric_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(numeric_level, int):
        print(f"ПРЕДУПРЕЖДЕНИЕ: Неверный LOG_LEVEL '{log_level_str}'. Используется INFO.", file=sys.stderr)
        numeric_level = logging.INFO
        log_level_str = "INFO" 

    root_logger = logging.getLogger() 

    if _logging_configured_globally and not force_reconfigure:
        root_logger.setLevel(numeric_level)
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level) 
        logging.info(f"Уровень логирования динамически обновлен на {log_level_str.upper()}.")
        return

    if force_reconfigure and root_logger.hasHandlers():
        logging.info("Принудительная перенастройка логирования. Удаление существующих обработчиков.")
        for handler in list(root_logger.handlers): 
            root_logger.removeHandler(handler)
            handler.close() 

    handlers = []

    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a') 
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)
    except Exception as e:
        print(f"ОШИБКА: Не удалось настроить файловый обработчик для '{log_file}': {e}", file=sys.stderr)

    # 2. Обработчик для консоли (stdout или stderr)
    stream_handler = logging.StreamHandler(sys.stdout) 
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S' 
    ))
    stream_handler.setLevel(numeric_level)
    handlers.append(stream_handler)
    
    if not root_logger.hasHandlers() or force_reconfigure:
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=handlers if handlers else None 
        )
    else: 
        root_logger.setLevel(numeric_level)



    _logging_configured_globally = True
    logging.info(f"Логирование настроено. Уровень: {log_level_str.upper()}. Файл: '{log_file if file_handler in handlers else 'N/A'}'")


logger = logging.getLogger(__name__)