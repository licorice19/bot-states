from .handlers import register_all_handlers
from .bot_logging import logger
from .middlewares import AdministatorMiddleware
from . import config
from telebot import TeleBot, StateMemoryStorage
import telebot.custom_filters


logger.setLevel(config.LOG_LEVEL)

logger.info("Application started")

state = StateMemoryStorage()
auth_middleware_instance = AdministatorMiddleware()

bot = TeleBot(config.TOKEN, parse_mode='HTML', use_class_middlewares=True, state_storage=state)

bot.setup_middleware(auth_middleware_instance)
bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

register_all_handlers(bot)

