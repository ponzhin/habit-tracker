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

    def completed_logs_count(self):
        """Количество выполненных отметок"""
        return self.logs.filter(completed=True).count()

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Если отметка о выполнении, проверяем достижения
        if self.completed:
            from .models import Achievement
            Achievement.check_and_create_achievements(self.habit)

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.habit.name} - {self.date}: {status}"

class ReminderSettings(models.Model):
    """Настройки напоминаний для пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reminder_settings')
    enabled = models.BooleanField(default=True, verbose_name='Включить напоминания')
    reminder_time = models.TimeField(default='09:00', verbose_name='Время напоминания')
    email_notifications = models.BooleanField(default=True, verbose_name='Email уведомления')
    telegram_notifications = models.BooleanField(default=False, verbose_name='Telegram уведомления')
    telegram_chat_id = models.CharField(max_length=100, blank=True, verbose_name='Telegram Chat ID')

    def __str__(self):
        return f"Напоминания для {self.user.username}"

class Achievement(models.Model):
    """Модель достижения"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200, verbose_name='Название достижения')
    description = models.TextField(verbose_name='Описание')
    streak_length = models.PositiveIntegerField(verbose_name='Длина серии')
    achieved_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True, verbose_name='Изображение')
    is_public = models.BooleanField(default=True, verbose_name='Публичное')

    class Meta:
        ordering = ['-achieved_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @classmethod
    def check_and_create_achievements(cls, habit):
        """Проверяем и создаем достижения для привычки"""
        streak = habit.get_current_streak()

        # Достижения за разные длины серий
        achievements_map = {
            7: "Первая неделя!",
            14: "Две недели подряд!",
            21: "Три недели! Формируется привычка!",
            30: "Месяц! Вы круты!",
            60: "Два месяца! Невероятно!",
            90: "Три месяца! Привычка сформирована!",
        }

        if streak in achievements_map and not cls.objects.filter(
            user=habit.user,
            habit=habit,
            streak_length=streak
        ).exists():
            # Создаем достижение
            achievement = cls.objects.create(
                user=habit.user,
                habit=habit,
                title=achievements_map[streak],
                description=f"Выполнял(а) привычку '{habit.name}' {streak} дней подряд!",
                streak_length=streak
            )
            return achievement

        return None