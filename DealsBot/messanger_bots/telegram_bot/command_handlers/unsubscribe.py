from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, \
    filters

from DealsBot.models import TelegramUser, DealSubscription

# Define states for the conversation
SUBSCRIPTION_SELECTION, CONFIRM_UNSUBSCRIBE = range(2)


async def start_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the unsubscribe process by showing the user's subscriptions."""
    user_id = update.effective_user.id

    # Fetch the user's subscriptions
    try:
        telegram_user = await sync_to_async(TelegramUser.objects.get, thread_sensitive=True)(user_id=user_id)
        subscriptions = await sync_to_async(list, thread_sensitive=True)(
            DealSubscription.objects.filter(profile=telegram_user.id)
        )
    except TelegramUser.DoesNotExist:
        subscriptions = []

    if not subscriptions:
        await update.message.reply_text("You don't have any subscriptions to unsubscribe from.")
        return ConversationHandler.END

    # Build inline keyboard with subscriptions
    keyboard = [
        [InlineKeyboardButton(f"{sub.product} ({sub.zipcode})", callback_data=f"unsubscribe:{sub.id}")]
        for sub in subscriptions
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a subscription to unsubscribe:", reply_markup=reply_markup)
    return SUBSCRIPTION_SELECTION


async def handle_subscription_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's selection and asks for confirmation."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    subscription_id = query.data.split(":")[1]
    context.user_data["subscription_id"] = subscription_id

    # Fetch the subscription details
    try:
        subscription = await sync_to_async(DealSubscription.objects.get, thread_sensitive=True)(id=subscription_id)
        context.user_data["subscription"] = subscription

        # Create a confirmation inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data=f"confirm_unsubscribe:{subscription_id}"),
                InlineKeyboardButton("No", callback_data="cancel_unsubscribe"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"You have selected: {subscription.product} ({subscription.zipcode}).\n"
                 "Do you want to unsubscribe?",
            reply_markup=reply_markup,
        )
        return CONFIRM_UNSUBSCRIBE
    except DealSubscription.DoesNotExist:
        await query.edit_message_text("The selected subscription no longer exists.")
        return ConversationHandler.END


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's confirmation to unsubscribe."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data.startswith("confirm_unsubscribe:"):
        subscription_id = query.data.split(":")[1]

        # Delete the subscription
        try:
            await sync_to_async(DealSubscription.objects.filter(id=subscription_id).delete, thread_sensitive=True)()
            await query.edit_message_text("You have successfully unsubscribed.")
        except Exception as e:
            await query.edit_message_text("An error occurred while unsubscribing. Please try again.")
        return ConversationHandler.END

    elif query.data == "cancel_unsubscribe":
        await query.edit_message_text("Unsubscribe process canceled.")
        return ConversationHandler.END


async def cancel_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the unsubscribe process."""
    await update.message.reply_text("Unsubscribe process canceled.")
    return ConversationHandler.END


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles unexpected input."""
    await update.message.reply_text(
        "I didn't understand that. Please use the provided buttons or /cancel to stop."
    )
    return ConversationHandler.END


unsubscribe_handler = ConversationHandler(
    entry_points=[CommandHandler("unsubscribe", start_unsubscribe)],
    states={
        SUBSCRIPTION_SELECTION: [
            CallbackQueryHandler(handle_subscription_selection, pattern=r"^unsubscribe:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, fallback),  # Handle unexpected text
        ],
        CONFIRM_UNSUBSCRIBE: [
            CallbackQueryHandler(handle_confirmation, pattern=r"^(confirm_unsubscribe|cancel_unsubscribe):?"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, fallback),  # Handle unexpected text
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_unsubscribe), MessageHandler(filters.ALL, fallback)],
)
