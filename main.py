from app import bot

import logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Telegram bot...")
    
    bot.polling(non_stop=True, interval=0)

    logger.info("Bot has stopped.")