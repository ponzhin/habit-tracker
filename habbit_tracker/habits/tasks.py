from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Habit, ReminderSettings
import logging
import time

logger = logging.getLogger(__name__)


def send_daily_reminders():
    """Отправка ежедневных напоминаний"""
    today = timezone.now().date()

    # Получаем всех пользователей с включенными напоминаниями
    reminder_settings = ReminderSettings.objects.filter(
        enabled=True,
        email_notifications=True
    )

    for settings in reminder_settings:
        user = settings.user
        current_time = timezone.now().time()

        # Проверяем время напоминания (плюс-минус 5 минут)
        reminder_time = settings.reminder_time
        time_diff = abs(
            (current_time.hour * 60 + current_time.minute) -
            (reminder_time.hour * 60 + reminder_time.minute)
        )

        if time_diff <= 5:  # Время для отправки
            # Получаем активные привычки пользователя
            habits = Habit.objects.filter(user=user, is_active=True)

            if not habits.exists():
                continue

            # Формируем список привычек для сегодня
            habits_to_remind = []
            for habit in habits:
                # Проверяем, не отмечена ли уже привычка сегодня
                already_logged = habit.logs.filter(date=today).exists()
                if not already_logged:
                    habits_to_remind.append(habit)

            if habits_to_remind:
                try:
                    # Отправляем email
                    subject = '⏰ Напоминание о привычках'

                    # Формируем список привычек
                    habit_list = '\n'.join([
                        f'• {habit.name}' for habit in habits_to_remind
                    ])

                    message = f'''
Привет, {user.username}!

Не забудьте выполнить свои привычки на сегодня:

{habit_list}

Текущая статистика:
{', '.join([f'{h.name}: {h.get_current_streak()} дней подряд' for h in habits])}

Перейдите в приложение, чтобы отметить выполнение:
http://localhost:8000/

Сделайте сегодняшний день продуктивным! 💪
                    '''

                    send_mail(
                        subject,
                        message.strip(),
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )

                    logger.info(f'Отправлено напоминание пользователю {user.email}')

                except Exception as e:
                    logger.error(f'Ошибка отправки напоминания: {e}')


def start_scheduler():
    """Запуск планировщика задач"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Добавляем задачу отправки напоминаний каждый час
    scheduler.add_job(
        send_daily_reminders,
        'interval',
        hours=1,
        id='daily_reminders',
        replace_existing=True
    )

    # Регистрируем события в Django
    register_events(scheduler)

    # Запускаем планировщик
    scheduler.start()
    logger.info("Планировщик задач запущен")

    try:
        # Это держит приложение живым
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Планировщик задач остановлен")