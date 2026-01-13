from django import forms
from .models import Achievement


class AchievementPostForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'image', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 30 дней без сахара!'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о своем достижении...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'image': 'Изображение (необязательно)',
            'is_public': 'Сделать публичной записью',
        }