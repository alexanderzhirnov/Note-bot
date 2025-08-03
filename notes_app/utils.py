from .models import User

def sync_telegram_user(telegram_id: str):
    """Синхронизирует пользователя между ботом и веб-интерфейсом"""
    return User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'username': f'tg_{telegram_id}', 'password': None}
    )