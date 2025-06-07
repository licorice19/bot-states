from telebot import BaseMiddleware, CancelUpdate
from telebot.types import Message
from . import config
import logging

logger = logging.getLogger(__name__)

class AdministatorMiddleware(BaseMiddleware):
    """
    Middleware to handle administrator commands.
    """
    def __init__(self):
        self.update_sensitive = True
        self.update_types = ['message', 'edited_message']
        self.unknown_users_access_attempts = {}

    def pre_process_message(self, message: Message, data):
        user_id = message.from_user.id if message.from_user and hasattr(message.from_user, 'id') else 'Unknown'
        if user_id == int(message.chat.id):
            if user_id not in config.ADMIN_IDS:
                full_name = message.from_user.full_name if message.from_user and hasattr(message.from_user, 'full_name') else 'Unknown'
                username = message.from_user.username if message.from_user and hasattr(message.from_user, 'username') else 'Unknown'
                user_id_str = str(user_id)
                logger.warning(f'''Unauthorized access attempt by user {user_id} in chat {message.chat.id}.\n
                               fullname: {full_name}\n
                               username: {username}\n''')
                if user_id_str in self.unknown_users_access_attempts:
                    self.unknown_users_access_attempts[user_id_str]['attempts'] += 1
                else:
                    self.unknown_users_access_attempts[user_id_str] = {
                        'username': username,
                        'full_name': full_name,
                        'attempts': 1,
                        'chat_id': message.chat.id # Сохраняем chat_id для информации
                    }
                return CancelUpdate()

    def post_process_message(self, message, data, exception):
        pass # only message update here for post_process

    def pre_process_edited_message(self, message: Message, data):
        if not message.from_user:
            return
        user_id = message.from_user.id
        if user_id == message.chat.id:
            if user_id not in config.ADMIN_IDS:
                logger.warning(f"Unauthorized access attempt (edited message) by user {user_id}")
                return CancelUpdate()

    def post_process_edited_message(self, message, data, exception):
        pass # only edited_message update here for post_process

