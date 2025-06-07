from telebot import TeleBot
from .middlewares import AdministatorMiddleware
from typing import Union

class AppTeleBot(TeleBot):
    """
    Кастомный класс TeleBot с дополнительными атрибутами.
    """
    auth_middleware_instance_ref: Union[AdministatorMiddleware, None]

    def __init__(self, token: str, *args, **kwargs):
        super().__init__(token, *args, **kwargs)
        # Инициализируем атрибут значением по умолчанию (например, None)
        self.auth_middleware_instance_ref = None