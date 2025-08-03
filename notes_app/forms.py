from django import forms
from django.utils import timezone
from .models import Note, Category, Tag

class NoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['tags'].queryset = Tag.objects.filter(user=user)
        
        # Улучшенная настройка виджета для deadline
        self.fields['deadline'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat()
            },
            format='%Y-%m-%d'
        )

    class Meta:
        model = Note
        fields = ['title', 'content', 'deadline', 'category', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Введите текст заметки...'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Введите заголовок...'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'deadline': 'Срок выполнения',
            'category': 'Категория',
            'tags': 'Теги',
        }
        help_texts = {
            'deadline': 'Укажите дату, когда нужно выполнить задачу',
            'tags': 'Выберите один или несколько тегов',
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Дата не может быть в прошлом")
        return deadline