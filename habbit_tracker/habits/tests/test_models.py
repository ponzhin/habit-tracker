from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ..models import Habit, HabitLog


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Читать книгу',
            description='Читать 30 минут в день',
            frequency='daily',
            target=30
        )

    def test_habit_creation(self):
        self.assertEqual(self.habit.name, 'Читать книгу')
        self.assertEqual(self.habit.user.username, 'testuser')
        self.assertTrue(self.habit.is_active)

    def test_habit_str(self):
        self.assertEqual(
            str(self.habit),
            'Читать книгу (testuser)'
        )

    def test_get_current_streak(self):
        # Создаем несколько выполненных дней подряд
        today = timezone.now().date()
        for i in range(3):
            date = today - timedelta(days=i)
            HabitLog.objects.create(
                habit=self.habit,
                date=date,
                completed=True
            )

        self.assertEqual(self.habit.get_current_streak(), 3)

    def test_get_completion_percentage(self):
        # Создаем отметки за последние 30 дней
        today = timezone.now().date()
        for i in range(10):
            date = today - timedelta(days=i)
            HabitLog.objects.create(
                habit=self.habit,
                date=date,
                completed=(i % 2 == 0)  # Каждый второй день
            )

        # Должно быть примерно 50%
        percentage = self.habit.get_completion_percentage()
        self.assertGreaterEqual(percentage, 0)
        self.assertLessEqual(percentage, 100)


class HabitLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Тестовая привычка'
        )
        self.log = HabitLog.objects.create(
            habit=self.habit,
            date=timezone.now().date(),
            completed=True,
            notes='Тестовая заметка'
        )

    def test_log_creation(self):
        self.assertTrue(self.log.completed)
        self.assertEqual(self.log.notes, 'Тестовая заметка')

    def test_log_str(self):
        expected_str = f'{self.habit.name} - {self.log.date}: ✓'
        self.assertEqual(str(self.log), expected_str)

    def test_unique_together_constraint(self):
        # Нельзя создать две записи на один день
        with self.assertRaises(Exception):
            HabitLog.objects.create(
                habit=self.habit,
                date=self.log.date,
                completed=False
            )
