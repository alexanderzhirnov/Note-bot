from django.conf import settings

def telegram_auth(request):
    return {
        'is_telegram_user': hasattr(request.user, 'telegram_id') and request.user.telegram_id,
        'telegram_login_url': f"/auth/telegram/?next={request.path}",
    }