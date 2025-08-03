import os
import asyncio
import logging
from django.core.management.base import BaseCommand
from notes_app.telegram_bot.bot import TelegramBot

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запускает Telegram бота для управления заметками'

    def handle(self, *args, **options):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            self.stderr.write('Ошибка: TELEGRAM_BOT_TOKEN не установлен в переменных окружения')
            return

        self.stdout.write('Запуск Telegram бота...')
        
        try:
            # Создаем и настраиваем event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Инициализируем и запускаем бота
            bot = TelegramBot(token)
            loop.run_until_complete(bot.start_polling())
            
        except KeyboardInterrupt:
            self.stdout.write('\nБот остановлен')
            loop.close()
        except Exception as e:
            logger.error(f'Ошибка при работе бота: {str(e)}')
            self.stderr.write(f'Ошибка: {str(e)}')
            if 'loop' in locals():
                loop.close()