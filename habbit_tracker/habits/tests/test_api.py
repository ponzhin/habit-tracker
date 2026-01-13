from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Habit, HabitLog
import json


class HabitAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Аутентифицируем пользователя
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        self.habit = Habit.objects.create(
            user=self.user,
            name='API Тест',
            description='Тестирование API',
            frequency='daily',
            target=30
        )

    def test_get_habits(self):
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DRF с пагинацией возвращает словарь с ключом 'results'
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            # Без пагинации - просто список
            self.assertEqual(len(response.data), 1)

    def test_create_habit(self):
        data = {
            'name': 'Новая привычка API',
            'description': 'Создана через API',
            'frequency': 'daily',
            'target': 21
        }
        response = self.client.post('/api/habits/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Новая привычка API')

    def test_update_habit(self):
        data = {'name': 'Обновленное название'}
        response = self.client.patch(f'/api/habits/{self.habit.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.name, 'Обновленное название')

    def test_delete_habit(self):
        response = self.client.delete(f'/api/habits/{self.habit.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_log_today_action(self):
        response = self.client.post(f'/api/habits/{self.habit.id}/log_today/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(HabitLog.objects.filter(habit=self.habit).exists())

    def test_get_statistics(self):
        # Создаем несколько логов
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        for i in range(3):
            HabitLog.objects.create(
                habit=self.habit,
                date=today - timedelta(days=i),
                completed=True
            )

        response = self.client.get(f'/api/habits/{self.habit.id}/statistics/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current_streak', response.data)
        self.assertIn('completion_rate', response.data)

    def test_get_dashboard(self):
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stats', response.data)
        self.assertIn('summary', response.data)
        self.assertIn('daily_stats', response.data)


class AuthenticationTest(TestCase):
    def test_token_auth(self):
        client = APIClient()
        user = User.objects.create_user(
            username='authuser',
            password='authpass123'
        )

        # Получение токена
        response = client.post('/api/auth/token/', {
            'username': 'authuser',
            'password': 'authpass123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        # Использование токена
        token = response.data['token']
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)