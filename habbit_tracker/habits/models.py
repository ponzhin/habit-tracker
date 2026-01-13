from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habit(models.Model):
    """Модель привычки"""
    DAILY = 'daily'
    WEEKLY = 'weekly'

    FREQUENCY_CHOICES = [
        (DAILY, 'Ежедневно'),
        (WEEKLY, 'Несколько раз в неделю'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=200, verbose_name='Название привычки')
    description = models.TextField(blank=True, verbose_name='Описание')
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default=DAILY,
        verbose_name='Периодичность'
    )
    target = models.PositiveIntegerField(
        default=30,
        verbose_name='Цель (дней подряд)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_current_streak(self):
        """Текущая серия выполненных дней подряд"""
        from django.db.models import Max

        # Находим последний пропущенный день
        last_missed = self.logs.filter(completed=False).aggregate(Max('date'))['date__max']

        if last_missed:
            # Если был пропуск, считаем от него
            streak_logs = self.logs.filter(date__gt=last_missed, completed=True).order_by('date')
        else:
            # Если пропусков не было, считаем все выполненные подряд
            streak_logs = self.logs.filter(completed=True).order_by('date')

        return streak_logs.count()

    def get_completion_percentage(self):
        """Процент выполнения за последние 30 дней"""
        from datetime import timedelta
        from django.utils import timezone

        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            total_days = 30  # Упрощаем: всегда 30 дней
            completed_days = self.logs.filter(
                date__range=[start_date, end_date],
                completed=True
            ).count()

            percentage = (completed_days / total_days) * 100 if total_days > 0 else 0
            return round(percentage)
        except:
            return 0


class HabitLog(models.Model):
    """Отметка о выполнении привычки за день"""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, verbose_name='Заметки')

    class Meta:
        unique_together = ['habit', 'date']  # Одна запись на день
        ordering = ['-date']

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.habit.name} - {self.date}: {status}"