import os

from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters, CommandHandler

from .command_handlers.search import search_handler
from .command_handlers.subscribe import subscribe_handler
from .command_handlers.unsubscribe import unsubscribe_handler
from .command_handlers.not_command import wildcard_handler


def run_telegram_bot():
    load_dotenv()
    telegram_bot_api_key = os.getenv("TELEGRAM_BOT_API_KEY")

    """Start the bot."""

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_bot_api_key).build()

    # Add handlers to the application
    application.add_handler(search_handler)
    application.add_handler(subscribe_handler)
    application.add_handler(unsubscribe_handler)
    application.add_handler(wildcard_handler)

    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    run_telegram_bot()
