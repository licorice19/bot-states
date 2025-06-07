from .handlers import register_all_handlers
from .bot_logging import setup_app_logging
from .middlewares import AdministatorMiddleware
from . import config
from telebot import TeleBot, StateMemoryStorage
import telebot.custom_filters
from typing import Union
from .entities import AppTeleBot

setup_app_logging(config.LOG_LEVEL)

import logging
app_logger = logging.getLogger(__name__)

app_logger.info("Initializing bot...")
app_logger.debug(f"Загруженные ADMIN_IDS: {config.ADMIN_IDS}")


state = StateMemoryStorage()
auth_middleware_instance = AdministatorMiddleware()



bot = AppTeleBot(config.TOKEN, parse_mode='HTML', use_class_middlewares=True, state_storage=state)

bot.auth_middleware_instance_ref = auth_middleware_instance

bot.setup_middleware(auth_middleware_instance)
bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

register_all_handlers(bot)

