from django.urls import path
from .views import (
    note_list, note_detail,
    note_create, note_edit,
    note_delete, export_notes,
    TelegramWidgetAuthView
)
from .views import register, note_list


urlpatterns = [
    path('notes/<int:pk>/', note_detail, name='note_detail'),
    path('notes/new/', note_create, name='note_create'),
    path('notes/<int:pk>/edit/', note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', note_delete, name='note_delete'),
    path('notes/export/', export_notes, name='export_notes'),
    path('auth/telegram/widget/', TelegramWidgetAuthView.as_view(), name='telegram_widget_auth'),
    path('accounts/register/', register, name='register'),
    path('', note_list, name='note_list'),  # главная страница - список заметок
]