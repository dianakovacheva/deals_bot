from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes


# Wildcard handler function
async def wildcard_handler_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = await context.bot.get_my_commands()
    commands = [f'/{command.command}' for command in commands]
    commands_list = '\n'.join(commands)
    await update.message.reply_text(f"Sorry, I didn't understand that. Please use:\n{commands_list}")


wildcard_handler = MessageHandler(filters.ALL, wildcard_handler_func)
