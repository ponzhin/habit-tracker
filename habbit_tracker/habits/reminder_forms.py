from django import forms
from .models import ReminderSettings


class ReminderSettingsForm(forms.ModelForm):
    reminder_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label='Время напоминания'
    )

    class Meta:
        model = ReminderSettings
        fields = ['enabled', 'reminder_time', 'email_notifications']
        widgets = {
            'enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'enabled': 'Включить напоминания',
            'email_notifications': 'Получать уведомления на email',
        }