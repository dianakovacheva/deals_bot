import re

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

from DealsBot.api_utils import fetch_offers, parse_response
from DealsBot.bot_functions.functions import prepare_telegram_message

# Define states for the conversation
PRODUCT, ZIP_CODE = range(2)


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the search process by asking for the product."""
    await update.message.reply_text("What product are you searching for?")
    return PRODUCT


async def ask_zip_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the product and asks for the zip code."""
    context.user_data['product'] = update.message.text
    await update.message.reply_text("Enter the zip code to search in.")
    return ZIP_CODE


async def perform_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        """Saves the zip code and performs the search."""
        context.user_data['zip_code'] = update.message.text
        product = context.user_data['product']
        zip_code = context.user_data['zip_code']

        # Check if valid zip code format
        validated_zip_code = re.match("^[0-9]{5}(?:-[0-9]{4})?$", zip_code)

        if validated_zip_code is None:
            await update.message.reply_text(
                f"The entered zip code '{zip_code}' is invalid. Please try again."
            )
            return ZIP_CODE
        else:
            deal = parse_response(fetch_offers(product, zip_code))
            search_params = {
                "product": product,
                "zipcode": zip_code
            }

            # Send error message
            if deal["totalResults"] <= 0:
                await update.message.reply_text(
                    f"No deals found for '{product}'."
                )
                return ConversationHandler.END
            else:
                formatted_message = prepare_telegram_message(deal=deal, search_params=search_params)

                # Here you can integrate your search logic.
                await update.message.reply_html(
                    formatted_message
                )

                # End the conversation
                return ConversationHandler.END
    except:
        await update.message.reply_text("There was a problem.")
        return ConversationHandler.END


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("Search canceled.")
    return ConversationHandler.END


# Create the ConversationHandler
search_handler = ConversationHandler(
    entry_points=[CommandHandler("search", start_search)],
    states={
        PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_zip_code)],
        ZIP_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_search)],
    },
    fallbacks=[CommandHandler("cancel", cancel_search)],
)
