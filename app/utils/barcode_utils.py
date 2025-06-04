# utils/barcode_utils.py
import random
import os
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image # Опционально для локального отображения
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def read_eans_from_file(filepath='codes.txt'):
    """
    Считывает EAN-коды из текстового файла.
    (Остается для возможного использования, но не используется в текущем боте для пользовательских кодов)
    """
    ean_codes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                code = line.strip()
                if code:
                    ean_codes.append(code)
        if not ean_codes:
            logger.warning(f"Файл '{filepath}' пуст или не содержит валидных строк.")
        return ean_codes
    except FileNotFoundError:
        logger.error(f"Файл '{filepath}' не найден.")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении файла '{filepath}': {e}", exc_info=True)
        return []

def generate_ean13_barcode_image_bytes(code_string: str) -> BytesIO | None:
    """
    Генерирует изображение штрих-кода EAN-13 для одной строки кода и возвращает его как BytesIO.

    Args:
        code_string (str): Код EAN-13 (12 или 13 цифр).

    Returns:
        BytesIO: Объект BytesIO с данными изображения PNG или None в случае ошибки.
    """
    if not (isinstance(code_string, str) and code_string.isdigit() and (len(code_string) == 12 or len(code_string) == 13)):
        logger.warning(f"Неверный формат кода EAN для генерации: {code_string}")
        return None

    try:
        image_bytes_io = BytesIO()
        # EAN13 требует строку. Библиотека сама рассчитает контрольную сумму для 12 цифр.
        my_ean = EAN13(str(code_string), writer=ImageWriter())
        my_ean.write(image_bytes_io) # Записывает PNG данные в BytesIO поток
        image_bytes_io.seek(0)       # Сбрасывает позицию потока в начало
        return image_bytes_io
    except Exception as e:
        logger.error(f"Ошибка генерации штрих-кода для '{code_string}': {e}", exc_info=True)
        return None

def parse_codes_input(text_input: str) -> list[str]:
    """
    Парсит строку с кодами, введенную пользователем.
    Коды могут быть разделены запятыми, пробелами или новыми строками.
    Возвращает список валидных кодов (12 или 13 цифр).
    """
    # Заменяем запятые и переносы строк на пробелы для упрощения разделения
    normalized_text = text_input.replace(',', ' ').replace('\n', ' ')
    
    potential_codes = [code.strip() for code in normalized_text.split(' ') if code.strip()]
    
    valid_codes = []
    for code in potential_codes:
        if code.isdigit() and (len(code) == 12 or len(code) == 13):
            valid_codes.append(code)
        else:
            logger.debug(f"Отфильтрован невалидный код: '{code}'")
            
    return valid_codes

# # Пример использования (если запускать как скрипт)
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG)
#     # Тест генерации одного штрих-кода
#     test_code = "123456789012" # 12 цифр, контрольная сумма будет добавлена
#     img_bytes = generate_ean13_barcode_image_bytes(test_code)
#     if img_bytes:
#         with open("test_barcode.png", "wb") as f:
#             f.write(img_bytes.read())
#         logger.info(f"Тестовый штрих-код сохранен как test_barcode.png для кода {test_code}")
#         # Попытка отобразить (требует Pillow)
#         # try:
#         #     img = Image.open("test_barcode.png")
#         #     img.show()
#         # except Exception as e:
#         #     logger.error(f"Не удалось отобразить изображение: {e}")
#     else:
#         logger.error(f"Не удалось сгенерировать штрих-код для {test_code}")

#     # Тест парсинга
#     test_input_codes = "111111111111, 2222222222222\n333333333333 abc 44444444444"
#     parsed = parse_codes_input(test_input_codes)
#     logger.info(f"Распарсенные коды: {parsed}") # Ожидаем: ['111111111111', '2222222222222', '333333333333']