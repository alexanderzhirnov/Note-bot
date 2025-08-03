from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from django.conf import settings
from .models import Note
from .utils import sync_telegram_user

async def handle_new_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, _ = sync_telegram_user(str(update.effective_user.id))
    Note.objects.create(
        user=user,
        title="Новая заметка",
        content=update.message.text
    )
    await update.message.reply_text("Заметка сохранена!")

def setup_bot_handlers(application):
    application.add_handler(CommandHandler("new", handle_new_note))