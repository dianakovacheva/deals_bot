from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

from DealsBot.db_utils.db_functions import create_telegram_user, create_deal
from DealsBot.models import TelegramUser, DealSubscription, Profile
from .search import ask_zip_code

# Define states for the conversation
PRODUCT, ZIP_CODE = range(2)


async def start_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the subscription process by asking for the product."""
    await update.message.reply_text("What product would you like to subscribe for?")
    return PRODUCT


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the zip code and performs the search."""
    context.user_data['zip_code'] = update.message.text.strip()
    product = context.user_data['product'].strip()
    zip_code = context.user_data['zip_code'].strip()

    user_id = update.effective_user.id
    username = update.effective_user.username
    user_first_name = update.effective_user.first_name
    user_last_name = update.effective_user.last_name
    chat_id = update.effective_chat.id

    # check if there is already a user with the given telegram user id
    #  existing_user = BotUser.objects.get(user_id=user_id)
    try:
        existing_user = await sync_to_async(TelegramUser.objects.get, thread_sensitive=True)(
            user_id=user_id)
    except TelegramUser.DoesNotExist:
        existing_user = None

    if existing_user:
        # get the corresponding Profile
        profile = await sync_to_async(Profile.objects.get, thread_sensitive=True)(id=existing_user.id)
        # Check if the user has already subscribed for this product
        try:
            existing_deal = await sync_to_async(DealSubscription.objects.get, thread_sensitive=True)(
                profile=profile,
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
        if existing_user.username != username:
            existing_user.username = username
            data_is_current = False
        if existing_user.user_first_name != user_first_name and user_first_name is not None:
            existing_user.user_first_name = user_first_name
            data_is_current = False
        if existing_user.user_last_name != user_last_name and user_last_name is not None:
            existing_user.user_last_name = user_last_name
            data_is_current = False
        if existing_user.chat_id != chat_id:
            existing_user.chat_id = chat_id
            data_is_current = False

        if not data_is_current:
            # existing_user.save()
            await sync_to_async(existing_user.save, thread_sensitive=True)()
    else:
        existing_user = await sync_to_async(
            create_telegram_user, thread_sensitive=True)(username, user_id, user_first_name,
                                                         user_last_name,
                                                         chat_id)

    # get the corresponding Profile
    profile = await sync_to_async(Profile.objects.get, thread_sensitive=True)(id=existing_user.id)

    created_subscription = await sync_to_async(create_deal, thread_sensitive=True)(
        product=product,
        zipcode=zip_code,
        communication_channels="telegram",
        profile=profile)

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
