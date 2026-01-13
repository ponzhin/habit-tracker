from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ReminderSettings


@receiver(post_save, sender=User)
def create_reminder_settings(sender, instance, created, **kwargs):
    """Автоматически создаем настройки напоминаний для нового пользователя"""
    if created:
        ReminderSettings.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_reminder_settings(sender, instance, **kwargs):
    """Сохраняем настройки напоминаний"""
    instance.reminder_settings.save()