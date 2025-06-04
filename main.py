from app import bot, logger

if __name__ == "__main__":
    logger.info("Bot is starting...")
    
    bot.polling()