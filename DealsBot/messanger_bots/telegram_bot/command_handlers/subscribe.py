from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

from DealsBot.db_utils.db_functions import create_bot_user, create_deal
from DealsBot.models import BotUser, DealSubscription
from .search import ask_zip_code

# Define states for the conversation
PRODUCT, ZIP_CODE = range(2)


async def start_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the subscription process by asking for the product."""
    await update.message.reply_text("What product would you like to subscribe for?")
    return PRODUCT


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the zip code and performs the search."""
    context.user_data['zip_code'] = update.message.text
    product = context.user_data['product']
    zip_code = context.user_data['zip_code']

    telegram_user_id = update.effective_user.id
    telegram_username = update.effective_user.username
    telegram_user_first_name = update.effective_user.first_name
    telegram_user_last_name = update.effective_user.last_name
    telegram_chat_id = update.effective_chat.id

    # check if there is already a user with the given telegram user id
    #  existing_user = BotUser.objects.get(telegram_user_id=telegram_user_id)
    try:
        existing_user = await sync_to_async(BotUser.objects.get, thread_sensitive=True)(
            telegram_user_id=telegram_user_id)
    except BotUser.DoesNotExist:
        existing_user = None

    if existing_user:
        # Check if the user has already subscribed for this product
        try:
            existing_deal = await sync_to_async(DealSubscription.objects.get, thread_sensitive=True)(
                bot_user=existing_user,
                product=product,
                zipcode=zip_code)
        except DealSubscription.DoesNotExist:
            existing_deal = None

        if existing_deal:
            await update.message.reply_text(f"You are already subscribed for {product} in {zip_code}.")
            # End the conversation
            return ConversationHandler.END
        # Check if the data for the user is current
        data_is_current = True
        if existing_user.telegram_username != telegram_username:
            existing_user.telegram_username = telegram_username
            data_is_current = False
        if existing_user.telegram_user_first_name != telegram_user_first_name and telegram_user_first_name is not None:
            existing_user.telegram_user_first_name = telegram_user_first_name
            data_is_current = False
        if existing_user.telegram_user_last_name != telegram_user_last_name and telegram_user_last_name is not None:
            existing_user.telegram_user_last_name = telegram_user_last_name
            data_is_current = False
        if existing_user.telegram_chat_id != telegram_chat_id:
            existing_user.telegram_chat_id = telegram_chat_id
            data_is_current = False

        if not data_is_current:
            # existing_user.save()
            await sync_to_async(existing_user.save, thread_sensitive=True)()
    else:
        # existing_user = create_bot_user(telegram_username, telegram_user_id, telegram_user_first_name,
        #                                 telegram_user_last_name,
        #                                 telegram_chat_id)

        existing_user = await sync_to_async(
            create_bot_user, thread_sensitive=True)(telegram_username, telegram_user_id, telegram_user_first_name,
                                                    telegram_user_last_name,
                                                    telegram_chat_id)

    # Create the subscription
    # created_subscription = create_deal(bot_user=existing_user,
    #                                    product=product,
    #                                    zipcode=zip_code,
    #                                    communication_channels="telegram")

    created_subscription = await sync_to_async(create_deal, thread_sensitive=True)(
        product=product,
        zipcode=zip_code,
        communication_channels="telegram",
        bot_user=existing_user,
        profile=None)

    if created_subscription:
        await update.message.reply_text(f"Successfully subscribed for {product} in {zip_code}.")
    else:
        await update.message.reply_text("There was a problem. Please try again.")

    # End the conversation
    return ConversationHandler.END


async def cancel_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("Subscribe canceled.")
    return ConversationHandler.END


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles unexpected input."""
    await update.message.reply_text(
        "I didn't understand that. Please use the provided buttons or /cancel to stop."
    )
    return ConversationHandler.END


# Create the ConversationHandler
subscribe_handler = ConversationHandler(
    entry_points=[CommandHandler("subscribe", start_subscription)],
    states={
        PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_zip_code)],
        ZIP_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, subscribe)],
    },
    fallbacks=[CommandHandler("cancel", cancel_subscribe), MessageHandler(filters.ALL, fallback)],
)
