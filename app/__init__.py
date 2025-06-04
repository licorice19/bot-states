from .handlers import register_all_handlers
from .bot_logging import logger
from .middleware import AdministatorMiddleware
from . import config
from telebot import TeleBot, StateMemoryStorage


logger.setLevel(config.LOG_LEVEL)

logger.info("Application started")

state = StateMemoryStorage()
middleware_instance = AdministatorMiddleware()

bot = TeleBot(config.TOKEN, parse_mode='HTML', use_class_middlewares=True, state_storage=state)

register_all_handlers(bot)

