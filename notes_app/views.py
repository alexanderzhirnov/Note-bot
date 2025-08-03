import logging
import json
import hmac
import hashlib
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth import login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm
from django.middleware.csrf import get_token
from rest_framework import viewsets, permissions
from .models import Note, Category, Tag, User
from .forms import NoteForm
from .serializers import NoteSerializer, CategorySerializer, TagSerializer
from django.urls import reverse

logger = logging.getLogger(__name__)


# =======================
# ========== API Views ==
# =======================
class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-created_at')

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)


# =======================
# ==== Telegram Widget JS 
# =======================
@method_decorator(csrf_exempt, name='dispatch')
class TelegramWidgetAuthView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            if not self.verify_telegram_data(data):
                return JsonResponse({'status': 'error', 'message': 'Invalid Telegram hash'}, status=403)

            telegram_id_str = str(data['id'])
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id_str,
                defaults={
                    'username': f"tg_{telegram_id_str}",
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                    'is_active': True
                }
            )

            if created:
                user.set_unusable_password()
                user.save()            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session.save()

            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('note_list'),
                'sessionid': request.session.session_key
            })

        except Exception as e:
            logger.error(f"TelegramWidgetAuth error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def verify_telegram_data(self, data):
        try:
            secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
            data_check_string = "\n".join(
                f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"
            )
            generated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
            return generated_hash == data['hash']
        except Exception as e:
            logger.error(f"verify_telegram_data error: {str(e)}")
            return False


# =======================
# ==== Telegram Redirect (через data-auth-url)
# =======================
class TelegramRedirectAuthView(View):
    def get(self, request):
        try:
            data = request.GET.dict()
            if not TelegramWidgetAuthView().verify_telegram_data(data):
                return redirect('telegram_login')

            telegram_id_str = str(data['id'])
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id_str,
                defaults={
                    'username': f"tg_{telegram_id_str}",
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                    'telegram_username': data.get('username', ''),
                    'password': None,
                    'is_active': True
                }
            )

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(reverse('note_list'))

        except Exception as e:
            logger.error(f"TelegramRedirectAuth error: {str(e)}")
            return redirect('telegram_login')


# =======================
# ========= Notes Views =
# =======================
@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notes/list.html', {
        'notes': notes,
        'categories': Category.objects.filter(user=request.user),
        'tags': Tag.objects.filter(user=request.user)
    })

@login_required
def note_detail(request, pk):
    note = Note.objects.get(pk=pk, user=request.user)
    return render(request, 'notes/detail.html', {'note': note})

@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            form.save_m2m()
            return redirect('note_list')
    else:
        form = NoteForm(user=request.user)
    return render(request, 'notes/form.html', {'form': form})

@login_required
def note_edit(request, pk):
    note = Note.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note, user=request.user)

    return render(request, 'notes/form.html', {
        'form': form,
        'is_telegram_user': hasattr(request.user, 'telegram_id'),
    })

@login_required
def note_delete(request, pk):
    note = Note.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('note_list')
    return render(request, 'notes/confirm_delete.html', {
        'note': note,
        'is_telegram_user': hasattr(request.user, 'telegram_id'),
    })

@login_required
def export_notes(request):
    notes = Note.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="notes_export.txt"'

    for note in notes:
        response.write(f"=== {note.title} ===\n")
        response.write(f"Created: {note.created_at}\n")
        if note.category:
            response.write(f"Category: {note.category.name}\n")
        if note.tags.exists():
            tags = ", ".join(tag.name for tag in note.tags.all())
            response.write(f"Tags: {tags}\n")
        response.write("\n")
        response.write(note.content)
        response.write("\n\n")

    return response


# =======================
# ========= Регистрация =
# =======================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
