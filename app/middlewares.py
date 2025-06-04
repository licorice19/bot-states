from telebot import BaseMiddleware, CancelUpdate
from . import config
import logging

logger = logging.getLogger(__name__)

class AdministatorMiddleware(BaseMiddleware):
    """
    Middleware to handle administrator commands.
    """
    def __init__(self):
        self.update_sensitive = True
        self.update_types = ['message', 'edited_message', 'callback_query']

    def pre_process_message(self, message, data):
        # only message update here
        if message.from_user.id == int(message.chat.id):
            if message.from_user.id not in config.ADMIN_IDS:
                logger.warning(f"Unauthorized access attempt by user {message.from_user.id} in chat {message.chat.id}")
                return CancelUpdate()

    def post_process_message(self, message, data, exception):
        pass # only message update here for post_process

    def pre_process_edited_message(self, message, data):
        # only edited_message update here
        pass

    def post_process_edited_message(self, message, data, exception):
        pass # only edited_message update here for post_process

