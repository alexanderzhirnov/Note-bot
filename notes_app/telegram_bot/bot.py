import os
import logging
import hashlib
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from notes_app.models import User, Note, Category, Tag
import datetime
from django.db import models
from typing import Optional
import asyncio
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.conf import settings
from notes_app.telegram_bot.utils import generate_telegram_auth_url

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = None
    
    async def start_polling(self):
        """Основной метод запуска бота"""
        self.application = Application.builder().token(self.token).build()
        self._register_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Бот запущен и ожидает сообщений...")
        while True:
            await asyncio.sleep(3600)

    def _register_handlers(self):
        """Регистрация обработчиков команд"""
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("new", self.new_note),
            CommandHandler("recent", self.recent_notes),
            CommandHandler("search", self.search_notes),
            CommandHandler("set_reminder", self.set_reminder),
            CommandHandler("web_login", self.web_login),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        ]
        for handler in handlers:
            self.application.add_handler(handler)
        self.application.add_error_handler(self.error_handler)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        user = update.effective_user
        if user is None:
            return
            
        telegram_id = str(user.id)
        
        user_obj, created = await sync_to_async(User.objects.get_or_create)(
            telegram_id=telegram_id,
            defaults={
                'username': user.username or f"tg_{telegram_id}",
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'telegram_username': user.username,
                'password': None  # Пароль не требуется для Telegram auth
            }
        )
        
        if created:
            await update.message.reply_text(
                f"Привет, {user.first_name}! Я бот для управления заметками.\n"
                "Используй /help для списка команд.\n"
                "Для доступа к веб-интерфейсу используй /web_login"
            )
        else:
            await update.message.reply_text(
                f"С возвращением, {user.first_name}! Чем могу помочь?\n"
                "Используй /help для списка команд.\n"
                "Для доступа к веб-интерфейсу используй /web_login"
            )
    
    async def web_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Генерация уникальной ссылки для входа"""
        user = await self._get_user(update)
        if user is None:
            return

        web_login_url = generate_telegram_auth_url(user.telegram_id)

        # Отправляем сообщение с кликабельной ссылкой
        await update.message.reply_text(
            text=(
                "🔐 <b>Ссылка для входа в веб-интерфейс:</b>\n"
                f"<a href='{web_login_url}'>Нажмите здесь для авторизации</a>\n\n"
                "⚠️ Ссылка действительна 5 минут"
            ),
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        # Генерация уникального токена с timestamp
        timestamp = str(int(timezone.now().timestamp()))
        secret = settings.SECRET_KEY
        token = hashlib.sha256(
            f"{user.telegram_id}{timestamp}{secret}".encode()
        ).hexdigest()

    async def web_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:      
        """Генерация уникальной ссылки для входа"""
        user = await self._get_user(update)
        if user is None:
            return

        web_login_url = generate_telegram_auth_url(user.telegram_id)

        await update.message.reply_text(
            "🔐 <b>Ссылка для входа в веб-интерфейс:</b>\n"
            f"<a href='{web_login_url}'>Нажмите здесь</a>\n\n"
            "⚠️ Ссылка действительна 5 минут",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        help_text = """
Доступные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/web_login - Получить ссылку для входа в веб-интерфейс
/new - Создать новую заметку
/recent - Показать последние 5 заметок
/search [текст] - Поиск заметок
/set_reminder [ID] [дата] - Установить напоминание
        """
        await update.message.reply_text(help_text)
    
    async def new_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /new"""
        user = await self._get_user(update)
        if user is None:
            return
            
        context.user_data['creating_note'] = True
        await update.message.reply_text("Введите заголовок заметки:")
    
    async def recent_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /recent"""
        user = await self._get_user(update)
        if user is None:
            return
            
        notes = await sync_to_async(list)(Note.objects.filter(user=user).order_by('-created_at')[:5])
        
        if not notes:
            await update.message.reply_text("У вас пока нет заметок.")
            return
        
        response = "Последние 5 заметок:\n\n"
        for note in notes:
            response += f"*{note.title}*\n"
            response += f"Создано: {note.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            if note.deadline:
                status = "⚠️ ПРОСРОЧЕНО" if note.is_overdue else "✅ Активно"
                response += f"Срок: {note.deadline.strftime('%Y-%m-%d')} {status}\n"
            tags = await sync_to_async(list)(note.tags.all())
            if tags:
                tag_names = ", ".join(tag.name for tag in tags)
                response += f"Теги: {tag_names}\n"
            response += "\n"
        
        await update.message.reply_text(response)
    
    async def search_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /search"""
        if not context.args:
            await update.message.reply_text("Пожалуйста, укажите текст для поиска: /search [текст]")
            return
            
        query = ' '.join(context.args)
        user = await self._get_user(update)
        if user is None:
            return
            
        notes = await sync_to_async(list)(
            Note.objects.filter(
                models.Q(user=user) &
                (models.Q(title__icontains=query) | 
                 models.Q(content__icontains=query) |
                 models.Q(tags__name__icontains=query))
            ).distinct().order_by('-created_at')[:10]
        )
        
        if not notes:
            await update.message.reply_text("Ничего не найдено.")
            return
        
        response = f"Результаты поиска по запросу '{query}':\n\n"
        for note in notes:
            response += f"*{note.title}*\n"
            response += f"Создано: {note.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            if note.category:
                response += f"Категория: {note.category.name}\n"
            tags = await sync_to_async(list)(note.tags.all())
            if tags:
                tag_names = ", ".join(tag.name for tag in tags)
                response += f"Теги: {tag_names}\n"
            response += "\n"
        
        await update.message.reply_text(response)
    
    async def set_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /set_reminder"""
        if len(context.args) < 2:
            await update.message.reply_text("Использование: /set_reminder [ID заметки] [дата в формате ГГГГ-ММ-ДД]")
            return
        
        note_id = context.args[0]
        date_str = context.args[1]
        user = await self._get_user(update)
        if user is None:
            return
        
        try:
            note = await sync_to_async(Note.objects.get)(id=note_id, user=user)
            deadline = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            note.deadline = timezone.make_aware(
                datetime.datetime.combine(deadline, datetime.time.min)
            )
            await sync_to_async(note.save)()
            
            await update.message.reply_text(
                f"Напоминание для заметки '{note.title}' установлено на {deadline.strftime('%Y-%m-%d')}"
            )
        except Note.DoesNotExist:
            await update.message.reply_text("Заметка не найдена.")
        except ValueError:
            await update.message.reply_text("Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений"""
        user = await self._get_user(update)
        if user is None or update.message is None:
            return
            
        text = update.message.text
        
        if context.user_data.get('creating_note'):
            if 'note_title' not in context.user_data:
                context.user_data['note_title'] = text
                await update.message.reply_text("Введите текст заметки:")
            else:
                note = await sync_to_async(Note.objects.create)(
                    title=context.user_data['note_title'],
                    content=text,
                    user=user
                )
                del context.user_data['creating_note']
                del context.user_data['note_title']
                await update.message.reply_text(f"Заметка '{note.title}' успешно создана!")
    
    async def _get_user(self, update: Update) -> Optional[User]:
        """Получаем пользователя по Telegram ID"""
        if update.effective_user is None:
            return None
            
        telegram_id = str(update.effective_user.id)
        try:
            return await sync_to_async(User.objects.get)(telegram_id=telegram_id)
        except User.DoesNotExist:
            logger.error(f"User {telegram_id} not found")
            return None

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик ошибок"""
        logger.error("Ошибка при обработке сообщения:", exc_info=context.error)
        
        if isinstance(update, Update) and update.message:
            await update.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте еще раз или обратитесь к администратору."
            )