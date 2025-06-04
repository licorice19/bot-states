import logging


logging.basicConfig(
    level=logging.INFO,  # Минимальный уровень сообщений для обработки (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    datefmt='%Y-%m-%d %H:%M:%S',  # Формат даты/времени
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),  # Вывод в файл app.log
        logging.StreamHandler()  # Вывод в консоль (по умолчанию sys.stderr)
    ]
)


logger = logging.getLogger(__name__)