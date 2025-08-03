from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from notes_app.views import TelegramWidgetAuthView
from notes_app.views import TelegramRedirectAuthView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(title="Notes API", default_version='v1'),
   public=True,)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Telegram Auth
    path('auth/telegram/', TemplateView.as_view(
        template_name='registration/telegram_login.html'
    ), name='telegram_login'),  # Изменено имя на telegram_login
    path('auth/telegram/widget/', TelegramWidgetAuthView.as_view(), name='telegram_widget_auth'),
    path('auth/telegram/complete/', TelegramRedirectAuthView.as_view(), name='telegram_redirect_auth'),
    path('', include('notes_app.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]