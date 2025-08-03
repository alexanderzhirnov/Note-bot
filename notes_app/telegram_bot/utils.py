from django.conf import settings
import hashlib
from django.utils import timezone

def generate_telegram_auth_url(telegram_id):
    """Генерация URL для авторизации через Telegram"""
    timestamp = str(int(timezone.now().timestamp()))
    secret = settings.SECRET_KEY
    token = hashlib.sha256(
        f"{telegram_id}{timestamp}{secret}".encode()
    ).hexdigest()
    return (
        f"{settings.WEBAPP_URL}/auth/telegram/"
        f"?telegram_id={telegram_id}"
        f"&token={token}"
        f"&timestamp={timestamp}"
    )