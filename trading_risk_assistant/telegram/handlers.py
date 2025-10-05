from telegram import Update
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to your Trading Risk Assistant Bot!\n\n"
        "Use /risk to start evaluating your trade.\n"
        "Use /cancel at any time to stop the process."
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/risk - Start a new risk evaluation\n"
        "/cancel - Cancel current operation\n"
        "/start - Welcome message\n"
        "/help - Show this help message"
    )
