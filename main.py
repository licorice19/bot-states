from app import bot, logger

if __name__ == "__main__":
    logger.info("Bot is starting...")
    
    bot.polling(non_stop=True, interval=0)

    logger.info("Bot has stopped.")