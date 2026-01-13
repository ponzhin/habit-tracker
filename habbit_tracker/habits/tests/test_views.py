from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Habit, HabitLog
from datetime import timedelta
from django.utils import timezone


class HabitViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Тестовая привычка'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая привычка')
        self.assertTemplateUsed(response, 'habits/index.html')

    def test_create_habit_view_get(self):
        response = self.client.get(reverse('create_habit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'habits/create_habit.html')

    def test_create_habit_view_post(self):
        data = {
            'name': 'Новая привычка',
            'description': 'Описание',
            'frequency': 'daily',
            'target': 21
        }
        response = self.client.post(reverse('create_habit'), data)

        # Должен редирект на главную
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

        # Проверяем, что привычка создалась
        self.assertTrue(Habit.objects.filter(name='Новая привычка').exists())

    def test_log_habit_view(self):
        url = reverse('log_habit', args=[self.habit.id])

        # GET запрос
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST запрос
        data = {'completed': True, 'notes': 'Тест'}
        response = self.client.post(url, data)

        if response.status_code == 302:
            self.assertRedirects(response, reverse('index'))
        else:
            self.assertEqual(response.status_code, 200)

        # Проверяем, что запись создалась
        today = timezone.now().date()
        self.assertTrue(
            HabitLog.objects.filter(
                habit=self.habit,
                date=today
            ).exists()
        )

    def test_calendar_view(self):
        url = reverse('calendar', args=[self.habit.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'habits/calendar.html')
        self.assertContains(response, self.habit.name)

    def test_statistics_view(self):
        # Создаем несколько логов для статистики
        today = timezone.now().date()
        for i in range(5):
            HabitLog.objects.create(
                habit=self.habit,
                date=today - timedelta(days=i),
                completed=(i % 2 == 0)
            )

        url = reverse('statistics', args=[self.habit.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'habits/statistics.html')

    def test_dashboard_view(self):
        url = reverse('dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'habits/dashboard.html')