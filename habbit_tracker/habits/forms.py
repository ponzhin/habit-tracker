from django import forms
from .models import Habit, HabitLog


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'frequency', 'target']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'target': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название привычки *',
            'description': 'Описание',
            'frequency': 'Периодичность',
            'target': 'Цель (дней подряд)',
        }


class HabitLogForm(forms.ModelForm):
    class Meta:
        model = HabitLog
        fields = ['completed', 'notes']
        widgets = {
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'completed': 'Выполнено сегодня',
            'notes': 'Заметки (необязательно)',
        }